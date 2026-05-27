"""
Polymarket Latency Arbitrage Bot - Configuration
Strategy: Monitor Binance price feed, detect lag in Polymarket pricing,
          execute binary option trades when edge > threshold.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    # ─── Polymarket ───────────────────────────────────────────────────────────
    POLY_PRIVATE_KEY: str = os.getenv("POLY_PRIVATE_KEY", "")
    POLY_API_KEY: str = os.getenv("POLY_API_KEY", "")
    POLY_API_SECRET: str = os.getenv("POLY_API_SECRET", "")
    POLY_API_PASSPHRASE: str = os.getenv("POLY_API_PASSPHRASE", "")
    POLY_CHAIN_ID: int = 137  # Polygon mainnet
    POLY_HOST: str = "https://clob.polymarket.com"
    POLY_GAMMA_HOST: str = "https://gamma-api.polymarket.com"

    # ─── Binance ──────────────────────────────────────────────────────────────
    BINANCE_WS_URL: str = "wss://stream.binance.com:9443/ws"
    BINANCE_SYMBOLS: list = field(default_factory=lambda: ["btcusdt", "ethusdt"])
    BINANCE_KLINE_INTERVAL: str = "1m"

    # ─── Arbitrage Parameters ─────────────────────────────────────────────────
    # Minimum edge (probability discrepancy) required to place a trade
    MIN_EDGE_THRESHOLD: float = 0.08        # 8% minimum edge
    # Time window (seconds) to look for price movement in Binance
    MOMENTUM_WINDOW_SECS: int = 30
    # Minimum % price move in Binance to trigger signal
    MIN_PRICE_MOVE_PCT: float = 0.003       # 0.3%
    # Maximum seconds remaining in a contract to still trade it
    MAX_TIME_REMAINING_SECS: int = 600      # 10 minutes
    # Minimum seconds remaining (avoid last-second fills)
    MIN_TIME_REMAINING_SECS: int = 60       # 1 minute

    # ─── Kelly Criterion & Position Sizing ────────────────────────────────────
    KELLY_FRACTION: float = 0.25            # Quarter-Kelly for safety
    MAX_POSITION_USDC: float = 500.0        # Hard cap per trade in USDC
    MIN_POSITION_USDC: float = 10.0         # Minimum trade size
    MAX_PORTFOLIO_RISK_PCT: float = 0.15    # Max 15% of capital in any single trade

    # ─── Risk Management ──────────────────────────────────────────────────────
    DAILY_LOSS_LIMIT_USDC: float = 200.0    # Kill switch: stop trading for the day
    MAX_OPEN_POSITIONS: int = 10            # Max simultaneous open trades
    MAX_DRAWDOWN_PCT: float = 0.20          # Stop all trading if drawdown > 20%
    CONSECUTIVE_LOSS_LIMIT: int = 8         # Stop after N consecutive losses

    # ─── Execution ────────────────────────────────────────────────────────────
    ORDER_TIMEOUT_SECS: int = 5             # Cancel unfilled orders after N seconds
    SLIPPAGE_TOLERANCE: float = 0.02        # Accept up to 2% worse than expected
    LATENCY_TARGET_MS: int = 200            # Target execution latency in ms

    # ─── Logging & Persistence ────────────────────────────────────────────────
    LOG_DIR: str = "./logs"
    TRADE_LOG_FILE: str = "./logs/trades.csv"
    PERFORMANCE_LOG_FILE: str = "./logs/performance.json"
    LOG_LEVEL: str = "INFO"

    # ─── Paper Trading ────────────────────────────────────────────────────────
    PAPER_TRADING: bool = True              # Set False for live trading
    PAPER_INITIAL_BALANCE: float = 1000.0  # Simulated starting capital


config = Config()
