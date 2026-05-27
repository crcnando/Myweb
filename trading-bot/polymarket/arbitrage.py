"""
Arbitrage Engine — the core alpha generation logic.

Strategy: Binance price moves → Polymarket hasn't updated yet → we exploit the lag.

When BTC moves significantly on Binance:
  1. Estimate the new "fair" probability of the contract outcome
  2. Compare to the current Polymarket price
  3. If the discrepancy (edge) > threshold → place a trade
  4. Kelly-size the position
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Optional

from binance_feed import BinanceFeed, MomentumSignal
from kelly import KellyResult, calculate_kelly, estimate_fair_probability
from polymarket_api import Market, PolymarketClient
from risk_manager import RiskManager, TradeRecord

logger = logging.getLogger(__name__)


@dataclass
class ArbitrageOpportunity:
    market: Market
    signal: MomentumSignal
    fair_prob: float
    market_prob: float
    edge: float
    kelly: KellyResult
    time_remaining: float


class ArbitrageEngine:
    """
    Listens to Binance momentum signals and scans open Polymarket
    contracts for pricing discrepancies.
    """

    def __init__(
        self,
        config,
        binance: BinanceFeed,
        polymarket: PolymarketClient,
        risk: RiskManager,
    ):
        self.config = config
        self.binance = binance
        self.polymarket = polymarket
        self.risk = risk
        self._opportunities_found: int = 0
        self._trades_executed: int = 0

        # Register signal handler
        binance.on_signal(self._on_binance_signal)

    async def _on_binance_signal(self, signal: MomentumSignal) -> None:
        """Called every time Binance shows a significant price move."""
        symbol = signal.symbol.replace("usdt", "").upper()  # btcusdt → BTC
        logger.info(
            f"[SIGNAL] {symbol} {signal.direction} {signal.magnitude_pct:.3%} "
            f"in {signal.duration_secs:.1f}s | confidence={signal.confidence:.2f}"
        )

        # Fetch active short-duration contracts for this symbol
        markets = self.polymarket.get_active_crypto_markets(
            symbol=symbol,
            max_duration_mins=int(self.config.MAX_TIME_REMAINING_SECS / 60),
        )

        now = time.time()
        for market in markets:
            time_remaining = market.end_time - now
            if time_remaining < self.config.MIN_TIME_REMAINING_SECS:
                continue

            opportunity = self._evaluate_opportunity(market, signal, time_remaining)
            if opportunity:
                await self._execute_opportunity(opportunity)

    def _evaluate_opportunity(
        self,
        market: Market,
        signal: MomentumSignal,
        time_remaining: float,
    ) -> Optional[ArbitrageOpportunity]:
        """
        Determine if there's a tradeable edge on this market given the Binance signal.
        Returns an ArbitrageOpportunity if edge > threshold, else None.
        """
        # Determine if market is "higher" or "lower" type
        question = market.question.lower()
        is_higher_contract = any(
            word in question for word in ["higher", "above", "up", "over", "exceed"]
        )
        is_lower_contract = any(
            word in question for word in ["lower", "below", "down", "under", "drop"]
        )

        if not is_higher_contract and not is_lower_contract:
            return None  # Can't determine contract direction

        # Estimate fair probability using Binance price and contract remaining time
        current_price = signal.current_price
        reference_price = signal.start_price  # Where price started in the window

        # P(BTC higher at expiry) given current position relative to contract strike
        fair_prob_higher = estimate_fair_probability(
            current_price=current_price,
            reference_price=reference_price,
            time_remaining_secs=int(time_remaining),
        )

        # For momentum signals, directional bias matters
        if signal.direction == "UP":
            fair_prob_higher = min(0.97, fair_prob_higher + signal.magnitude_pct * 2)
        else:
            fair_prob_higher = max(0.03, fair_prob_higher - signal.magnitude_pct * 2)

        # Map to the market's contract direction
        if is_higher_contract:
            fair_prob = fair_prob_higher
            market_prob = market.yes_price
        else:
            fair_prob = 1.0 - fair_prob_higher
            market_prob = market.yes_price

        # Check minimum confidence
        if signal.confidence < 0.6:
            return None

        balance = self._current_balance()
        kelly = calculate_kelly(
            fair_prob=fair_prob,
            market_prob=market_prob,
            bankroll=balance,
            kelly_fraction=self.config.KELLY_FRACTION,
            max_position=self.config.MAX_POSITION_USDC,
            min_position=self.config.MIN_POSITION_USDC,
        )

        if kelly is None:
            return None

        if abs(kelly.edge) < self.config.MIN_EDGE_THRESHOLD:
            return None

        self._opportunities_found += 1
        logger.info(
            f"[EDGE] {market.question[:60]} | "
            f"fair={fair_prob:.3f} market={market_prob:.3f} "
            f"edge={kelly.edge:+.3f} | "
            f"size=${kelly.position_usdc:.2f} {kelly.side} | "
            f"EV={kelly.expected_value:.3f}"
        )

        return ArbitrageOpportunity(
            market=market,
            signal=signal,
            fair_prob=fair_prob,
            market_prob=market_prob,
            edge=kelly.edge,
            kelly=kelly,
            time_remaining=time_remaining,
        )

    async def _execute_opportunity(self, opp: ArbitrageOpportunity) -> None:
        """Pass through risk checks and fire the order."""
        allowed, reason = self.risk.can_trade(
            size_usdc=opp.kelly.position_usdc,
            symbol=opp.signal.symbol,
            edge=opp.edge,
        )

        if not allowed:
            logger.warning(f"Trade blocked by risk manager: {reason}")
            return

        # Determine which token to buy
        if opp.kelly.side == "YES":
            token_id = opp.market.yes_token_id
            price = opp.market.yes_price
        else:
            token_id = opp.market.no_token_id
            price = opp.market.no_price

        # Execute order
        result = self.polymarket.place_market_order(
            token_id=token_id,
            side="BUY",
            size_usdc=opp.kelly.position_usdc,
            price=price,
            paper=self.config.PAPER_TRADING,
        )

        if not result.success:
            logger.error(f"Order failed: {result.error}")
            return

        # Register with risk manager
        trade = TradeRecord(
            trade_id=result.order_id or str(uuid.uuid4()),
            symbol=opp.signal.symbol.upper(),
            market_question=opp.market.question,
            side=opp.kelly.side,
            size_usdc=opp.kelly.position_usdc,
            entry_price=result.filled_price or price,
            edge_at_entry=opp.edge,
            kelly_fraction=opp.kelly.kelly_scaled,
        )
        self.risk.register_trade(trade)
        self._trades_executed += 1

        mode = "PAPER" if self.config.PAPER_TRADING else "LIVE"
        logger.info(
            f"[{mode}] Executed: {opp.kelly.side} ${opp.kelly.position_usdc:.2f} | "
            f"{opp.market.question[:50]} | "
            f"latency={result.latency_ms:.0f}ms"
        )

    def _current_balance(self) -> float:
        if self.config.PAPER_TRADING:
            return self.risk.get_stats().get("balance", self.config.PAPER_INITIAL_BALANCE)
        return self.polymarket.get_balance()

    def get_stats(self) -> dict:
        return {
            "opportunities_found": self._opportunities_found,
            "trades_executed": self._trades_executed,
            "conversion_rate": (
                self._trades_executed / self._opportunities_found
                if self._opportunities_found > 0 else 0
            ),
        }
