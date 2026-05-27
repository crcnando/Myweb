"""
Risk Manager — the kill switch layer.
Every trade must pass through here before execution.
Tracks daily PnL, drawdown, consecutive losses, and open exposure.
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    trade_id: str
    symbol: str
    market_question: str
    side: str                # "YES" or "NO"
    size_usdc: float
    entry_price: float
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    status: str = "OPEN"     # OPEN | CLOSED | CANCELLED
    opened_at: float = field(default_factory=time.time)
    closed_at: Optional[float] = None
    edge_at_entry: float = 0.0
    kelly_fraction: float = 0.0


class RiskManager:
    """
    Central risk control. Acts as a gatekeeper before any order reaches the market.
    Implements hard stops that cannot be overridden by the strategy logic.
    """

    def __init__(self, config):
        self.config = config
        self._open_trades: dict[str, TradeRecord] = {}
        self._closed_trades: list[TradeRecord] = []
        self._daily_pnl: float = 0.0
        self._peak_balance: float = config.PAPER_INITIAL_BALANCE
        self._current_balance: float = config.PAPER_INITIAL_BALANCE
        self._consecutive_losses: int = 0
        self._trading_halted: bool = False
        self._halt_reason: str = ""
        self._day_start: float = self._today_start()
        self._trades_today: int = 0
        os.makedirs(config.LOG_DIR, exist_ok=True)

    @staticmethod
    def _today_start() -> float:
        import datetime
        today = datetime.date.today()
        return time.mktime(today.timetuple())

    def _reset_daily_if_needed(self) -> None:
        if time.time() > self._day_start + 86400:
            logger.info(f"New trading day. Daily PnL reset. Yesterday: ${self._daily_pnl:.2f}")
            self._daily_pnl = 0.0
            self._trades_today = 0
            self._day_start = self._today_start()
            # Re-enable trading on new day (unless drawdown kill is active)
            drawdown = (self._peak_balance - self._current_balance) / self._peak_balance
            if drawdown < self.config.MAX_DRAWDOWN_PCT and "drawdown" not in self._halt_reason:
                self._trading_halted = False
                self._halt_reason = ""
                self._consecutive_losses = 0

    def can_trade(
        self,
        size_usdc: float,
        symbol: str,
        edge: float,
    ) -> tuple[bool, str]:
        """
        Returns (allowed, reason). If not allowed, reason explains why.
        """
        self._reset_daily_if_needed()

        if self._trading_halted:
            return False, f"Trading halted: {self._halt_reason}"

        if self._daily_pnl <= -self.config.DAILY_LOSS_LIMIT_USDC:
            self._halt("Daily loss limit reached")
            return False, self._halt_reason

        drawdown = (self._peak_balance - self._current_balance) / max(self._peak_balance, 1)
        if drawdown >= self.config.MAX_DRAWDOWN_PCT:
            self._halt(f"Max drawdown {drawdown:.1%} exceeded")
            return False, self._halt_reason

        if self._consecutive_losses >= self.config.CONSECUTIVE_LOSS_LIMIT:
            self._halt(f"{self._consecutive_losses} consecutive losses")
            return False, self._halt_reason

        open_count = len([t for t in self._open_trades.values() if t.symbol == symbol])
        if len(self._open_trades) >= self.config.MAX_OPEN_POSITIONS:
            return False, "Max open positions reached"

        if size_usdc > self._current_balance * self.config.MAX_PORTFOLIO_RISK_PCT:
            size_usdc = self._current_balance * self.config.MAX_PORTFOLIO_RISK_PCT
            logger.warning(f"Position size capped to {size_usdc:.2f} USDC (portfolio risk limit)")

        if size_usdc < self.config.MIN_POSITION_USDC:
            return False, f"Size {size_usdc:.2f} below minimum {self.config.MIN_POSITION_USDC}"

        return True, "OK"

    def register_trade(self, trade: TradeRecord) -> None:
        self._open_trades[trade.trade_id] = trade
        self._trades_today += 1
        logger.info(
            f"Trade registered: {trade.trade_id} | {trade.side} {trade.size_usdc:.2f} USDC "
            f"@ {trade.entry_price:.3f} | edge={trade.edge_at_entry:.3f}"
        )

    def close_trade(self, trade_id: str, exit_price: float) -> Optional[TradeRecord]:
        trade = self._open_trades.pop(trade_id, None)
        if not trade:
            return None

        trade.exit_price = exit_price
        trade.closed_at = time.time()
        trade.status = "CLOSED"

        # PnL calculation for binary contract
        if trade.side == "YES":
            # Bought YES at entry_price, contract resolved at exit_price (0.0 or 1.0 at expiry)
            pnl = (exit_price - trade.entry_price) * (trade.size_usdc / trade.entry_price)
        else:
            # Bought NO at (1 - entry_price)
            no_entry = 1.0 - trade.entry_price
            pnl = (exit_price - no_entry) * (trade.size_usdc / no_entry)

        trade.pnl = pnl
        self._daily_pnl += pnl
        self._current_balance += pnl

        if pnl > 0:
            self._consecutive_losses = 0
            if self._current_balance > self._peak_balance:
                self._peak_balance = self._current_balance
        else:
            self._consecutive_losses += 1

        self._closed_trades.append(trade)
        self._log_trade(trade)

        logger.info(
            f"Trade closed: {trade_id} | PnL=${pnl:+.2f} | "
            f"Balance=${self._current_balance:.2f} | Daily PnL=${self._daily_pnl:+.2f}"
        )

        return trade

    def _halt(self, reason: str) -> None:
        self._trading_halted = True
        self._halt_reason = reason
        logger.critical(f"TRADING HALTED: {reason}")

    def _log_trade(self, trade: TradeRecord) -> None:
        import csv
        file_exists = os.path.exists(self.config.TRADE_LOG_FILE)
        with open(self.config.TRADE_LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "trade_id", "symbol", "question", "side", "size_usdc",
                    "entry_price", "exit_price", "pnl", "edge_at_entry",
                    "opened_at", "closed_at", "duration_secs"
                ])
            duration = (trade.closed_at or 0) - trade.opened_at
            writer.writerow([
                trade.trade_id, trade.symbol, trade.market_question[:50],
                trade.side, f"{trade.size_usdc:.2f}",
                f"{trade.entry_price:.4f}", f"{trade.exit_price:.4f}",
                f"{trade.pnl:.4f}", f"{trade.edge_at_entry:.4f}",
                f"{trade.opened_at:.0f}", f"{trade.closed_at:.0f}",
                f"{duration:.0f}"
            ])

    def get_stats(self) -> dict:
        closed = self._closed_trades
        if not closed:
            return {
                "balance": self._current_balance,
                "daily_pnl": self._daily_pnl,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "open_positions": len(self._open_trades),
                "halted": self._trading_halted,
            }

        wins = [t for t in closed if (t.pnl or 0) > 0]
        losses = [t for t in closed if (t.pnl or 0) <= 0]
        avg_win = sum(t.pnl for t in wins) / len(wins) if wins else 0
        avg_loss = sum(abs(t.pnl) for t in losses) / len(losses) if losses else 0
        profit_factor = (sum(t.pnl for t in wins) / sum(abs(t.pnl) for t in losses)
                         if losses and sum(abs(t.pnl) for t in losses) > 0 else 0)

        return {
            "balance": self._current_balance,
            "daily_pnl": self._daily_pnl,
            "total_trades": len(closed),
            "open_positions": len(self._open_trades),
            "win_rate": len(wins) / len(closed) if closed else 0,
            "avg_win_usdc": avg_win,
            "avg_loss_usdc": avg_loss,
            "profit_factor": profit_factor,
            "consecutive_losses": self._consecutive_losses,
            "max_drawdown_pct": (self._peak_balance - self._current_balance) / self._peak_balance,
            "halted": self._trading_halted,
            "halt_reason": self._halt_reason,
        }

    def print_stats(self) -> None:
        s = self.get_stats()
        print("\n" + "═" * 50)
        print("  TRADING BOT PERFORMANCE")
        print("═" * 50)
        print(f"  Balance:        ${s['balance']:,.2f}")
        print(f"  Daily PnL:      ${s['daily_pnl']:+,.2f}")
        print(f"  Total Trades:   {s['total_trades']}")
        print(f"  Open:           {s['open_positions']}")
        print(f"  Win Rate:       {s.get('win_rate', 0):.1%}")
        print(f"  Profit Factor:  {s.get('profit_factor', 0):.2f}")
        print(f"  Consec. Losses: {s['consecutive_losses']}")
        print(f"  Max Drawdown:   {s.get('max_drawdown_pct', 0):.1%}")
        if s["halted"]:
            print(f"  ⚠  HALTED: {s['halt_reason']}")
        print("═" * 50 + "\n")
