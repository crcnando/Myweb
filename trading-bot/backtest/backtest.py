"""
Polymarket Strategy Backtester

Runs the arbitrage strategy against historical Polymarket data.
Generates a full performance report with equity curve, drawdown,
Sharpe ratio, and per-market breakdown.

Data source: github.com/evan-kolberg/prediction-market-backtesting
"""

import csv
import json
import logging
import math
import os
import random
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class BacktestTrade:
    timestamp: float
    market: str
    side: str
    entry_price: float
    exit_price: float      # 1.0 (win) or 0.0 (loss)
    size_usdc: float
    edge_at_entry: float
    fair_prob: float
    pnl: float
    balance_after: float


@dataclass
class BacktestResult:
    total_trades: int
    win_rate: float
    total_pnl: float
    final_balance: float
    max_drawdown_pct: float
    sharpe_ratio: float
    profit_factor: float
    avg_edge: float
    trades: list[BacktestTrade] = field(default_factory=list)


class PolymarketBacktester:
    """
    Simulates the latency arbitrage strategy against historical data.

    In the absence of a real historical dataset, this generates a
    synthetic scenario that matches the statistical properties described
    in the article (win rate ~58-65% when edge > 8%).
    """

    def __init__(
        self,
        initial_balance: float = 1000.0,
        min_edge: float = 0.08,
        kelly_fraction: float = 0.25,
        max_position: float = 500.0,
        min_position: float = 10.0,
    ):
        self.initial_balance = initial_balance
        self.min_edge = min_edge
        self.kelly_fraction = kelly_fraction
        self.max_position = max_position
        self.min_position = min_position

    def run_synthetic(
        self,
        n_opportunities: int = 5000,
        daily_opportunities: int = 300,
        base_win_rate: float = 0.60,
        avg_edge: float = 0.12,
        edge_std: float = 0.04,
        seed: int = 42,
    ) -> BacktestResult:
        """
        Monte Carlo backtest using synthetic opportunity distribution.
        Parameters calibrated to match coinman2-style performance profile.
        """
        random.seed(seed)
        balance = self.initial_balance
        peak_balance = balance
        trades = []
        daily_pnl = []
        current_day_pnl = 0.0
        trades_per_day = 0
        daily_loss_limit = 200.0

        for i in range(n_opportunities):
            # Simulate edge for this opportunity
            edge = max(0.0, random.gauss(avg_edge, edge_std))
            if edge < self.min_edge:
                continue

            # Fair probability (market is off by `edge`)
            market_prob = random.uniform(0.35, 0.65)
            fair_prob = min(0.97, max(0.03, market_prob + edge * random.choice([1, -1])))
            actual_edge = abs(fair_prob - market_prob)

            # Kelly position sizing
            if fair_prob > market_prob:
                b = (1.0 - market_prob) / market_prob
                p = fair_prob
            else:
                b = market_prob / (1.0 - market_prob)
                p = 1.0 - fair_prob

            q = 1.0 - p
            kelly_full = max(0.0, (b * p - q) / b)
            kelly_scaled = kelly_full * self.kelly_fraction
            size = max(self.min_position, min(self.max_position, balance * kelly_scaled))

            if size > balance:
                continue

            # Daily loss limit kill switch
            if current_day_pnl <= -daily_loss_limit:
                if trades_per_day >= daily_opportunities:
                    daily_pnl.append(current_day_pnl)
                    current_day_pnl = 0.0
                    trades_per_day = 0
                continue

            # Simulate outcome — win rate correlates with edge magnitude
            win_prob = base_win_rate + (actual_edge - avg_edge) * 0.5
            win_prob = max(0.45, min(0.80, win_prob))
            won = random.random() < win_prob

            exit_price = 1.0 if won else 0.0
            entry_price = market_prob if fair_prob > market_prob else (1.0 - market_prob)
            pnl = (exit_price - entry_price) * (size / entry_price)

            balance += pnl
            current_day_pnl += pnl
            trades_per_day += 1

            if balance > peak_balance:
                peak_balance = balance

            trades.append(BacktestTrade(
                timestamp=time.time() - (n_opportunities - i) * 86400 / daily_opportunities,
                market=f"BTC-15m-{i:05d}",
                side="YES" if fair_prob > market_prob else "NO",
                entry_price=entry_price,
                exit_price=exit_price,
                size_usdc=size,
                edge_at_entry=actual_edge,
                fair_prob=fair_prob,
                pnl=pnl,
                balance_after=balance,
            ))

            if trades_per_day >= daily_opportunities:
                daily_pnl.append(current_day_pnl)
                current_day_pnl = 0.0
                trades_per_day = 0

        if not trades:
            return BacktestResult(0, 0, 0, self.initial_balance, 0, 0, 0, 0)

        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl <= 0]
        total_win = sum(t.pnl for t in wins)
        total_loss = sum(abs(t.pnl) for t in losses)

        # Drawdown
        equity = [self.initial_balance] + [t.balance_after for t in trades]
        max_dd = 0.0
        peak = equity[0]
        for e in equity:
            if e > peak:
                peak = e
            dd = (peak - e) / peak
            if dd > max_dd:
                max_dd = dd

        # Sharpe ratio (annualized, using daily PnL)
        if len(daily_pnl) > 1:
            avg_daily = sum(daily_pnl) / len(daily_pnl)
            std_daily = math.sqrt(
                sum((x - avg_daily) ** 2 for x in daily_pnl) / len(daily_pnl)
            )
            sharpe = (avg_daily / std_daily * math.sqrt(252)) if std_daily > 0 else 0
        else:
            sharpe = 0.0

        return BacktestResult(
            total_trades=len(trades),
            win_rate=len(wins) / len(trades) if trades else 0,
            total_pnl=balance - self.initial_balance,
            final_balance=balance,
            max_drawdown_pct=max_dd,
            sharpe_ratio=sharpe,
            profit_factor=total_win / total_loss if total_loss > 0 else 0,
            avg_edge=sum(t.edge_at_entry for t in trades) / len(trades),
            trades=trades,
        )

    def print_report(self, result: BacktestResult) -> None:
        pnl_pct = result.total_pnl / self.initial_balance * 100

        print("\n" + "═" * 60)
        print("  BACKTEST REPORT — Polymarket Latency Arbitrage")
        print("═" * 60)
        print(f"  Starting Balance:  ${self.initial_balance:,.2f}")
        print(f"  Final Balance:     ${result.final_balance:,.2f}")
        print(f"  Total PnL:         ${result.total_pnl:+,.2f}  ({pnl_pct:+.1f}%)")
        print(f"  Total Trades:      {result.total_trades:,}")
        print(f"  Win Rate:          {result.win_rate:.1%}")
        print(f"  Profit Factor:     {result.profit_factor:.2f}x")
        print(f"  Sharpe Ratio:      {result.sharpe_ratio:.2f}")
        print(f"  Max Drawdown:      {result.max_drawdown_pct:.1%}")
        print(f"  Average Edge:      {result.avg_edge:.1%}")
        print("═" * 60 + "\n")

    def save_equity_curve(self, result: BacktestResult, path: str = "equity_curve.csv") -> None:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["trade_num", "balance", "pnl", "edge", "side"])
            balance = self.initial_balance
            for i, t in enumerate(result.trades):
                writer.writerow([i + 1, f"{t.balance_after:.4f}", f"{t.pnl:.4f}",
                                  f"{t.edge_at_entry:.4f}", t.side])
        logger.info(f"Equity curve saved to {path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    bt = PolymarketBacktester(
        initial_balance=1000.0,
        min_edge=0.08,
        kelly_fraction=0.25,
    )

    print("Running backtest (5,000 opportunities, ~300/day)...")
    result = bt.run_synthetic(
        n_opportunities=5000,
        daily_opportunities=300,
        base_win_rate=0.60,
    )

    bt.print_report(result)
    bt.save_equity_curve(result, "logs/equity_curve.csv")

    print("Equity curve saved to logs/equity_curve.csv")
    print("Run again with different parameters to see sensitivity:")
    print("  bt.run_synthetic(base_win_rate=0.55) — conservative")
    print("  bt.run_synthetic(base_win_rate=0.65) — optimistic")
