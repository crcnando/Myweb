"""
Main bot entry point.
Wires all layers together and runs the event loop.

Usage:
  # Paper trading (safe, no real money):
  python bot.py

  # Live trading (requires real API keys in .env):
  PAPER_TRADING=false python bot.py
"""

import asyncio
import logging
import os
import signal
import sys

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import config
from binance_feed import BinanceFeed
from polymarket_api import PolymarketClient
from risk_manager import RiskManager
from arbitrage import ArbitrageEngine

# ─── Logging ─────────────────────────────────────────────────────────────────
os.makedirs(config.LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)-5s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"{config.LOG_DIR}/bot.log"),
    ],
)
logger = logging.getLogger("bot")


async def stats_reporter(risk: RiskManager, engine: ArbitrageEngine) -> None:
    """Print a performance summary every 5 minutes."""
    while True:
        await asyncio.sleep(300)
        risk.print_stats()
        engine_stats = engine.get_stats()
        logger.info(
            f"Engine: {engine_stats['opportunities_found']} opportunities, "
            f"{engine_stats['trades_executed']} executed "
            f"({engine_stats['conversion_rate']:.1%} conversion)"
        )


async def main() -> None:
    mode = "PAPER" if config.PAPER_TRADING else "LIVE"
    logger.info(f"Starting Polymarket Latency Arbitrage Bot [{mode}]")
    logger.info(f"Symbols: {config.BINANCE_SYMBOLS}")
    logger.info(f"Min edge: {config.MIN_EDGE_THRESHOLD:.0%} | Kelly fraction: {config.KELLY_FRACTION}")

    # ── Layer 1: Data feed ────────────────────────────────────────────────────
    binance = BinanceFeed(
        symbols=config.BINANCE_SYMBOLS,
        momentum_window_secs=config.MOMENTUM_WINDOW_SECS,
        min_move_pct=config.MIN_PRICE_MOVE_PCT,
    )

    # ── Layer 2: Exchange client ──────────────────────────────────────────────
    polymarket = PolymarketClient(config)
    if not config.PAPER_TRADING:
        if not polymarket.initialize():
            logger.error("Failed to initialize Polymarket client. Exiting.")
            return
    else:
        logger.info("Paper trading mode: Polymarket client not connected")

    # ── Layer 3: Risk ─────────────────────────────────────────────────────────
    risk = RiskManager(config)

    # ── Layer 4: Alpha engine ─────────────────────────────────────────────────
    engine = ArbitrageEngine(config, binance, polymarket, risk)

    # ── Graceful shutdown ─────────────────────────────────────────────────────
    loop = asyncio.get_event_loop()

    def shutdown(sig, frame):
        logger.info(f"Received {sig.name}. Shutting down...")
        risk.print_stats()
        for task in asyncio.all_tasks(loop):
            task.cancel()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # ── Run ───────────────────────────────────────────────────────────────────
    logger.info("Bot running. Press Ctrl+C to stop.")
    risk.print_stats()

    try:
        await asyncio.gather(
            binance.run(),
            stats_reporter(risk, engine),
        )
    except asyncio.CancelledError:
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
