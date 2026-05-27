"""
Binance Real-Time Price Feed via WebSocket.
Maintains a rolling price history and computes momentum signals.
"""

import asyncio
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Optional

import websockets

logger = logging.getLogger(__name__)


@dataclass
class PriceTick:
    symbol: str
    price: float
    timestamp: float  # Unix seconds
    volume_24h: float = 0.0
    bid: float = 0.0
    ask: float = 0.0


@dataclass
class MomentumSignal:
    symbol: str
    direction: str          # "UP" or "DOWN"
    magnitude_pct: float    # % price change in window
    duration_secs: float    # How long the move took
    current_price: float
    start_price: float
    confidence: float       # 0.0 - 1.0 based on consistency


class BinanceFeed:
    """
    Connects to Binance WebSocket and maintains real-time price history.
    Fires callbacks when a momentum signal is detected.
    """

    def __init__(
        self,
        symbols: list[str],
        momentum_window_secs: int = 30,
        min_move_pct: float = 0.003,
    ):
        self.symbols = [s.lower() for s in symbols]
        self.momentum_window_secs = momentum_window_secs
        self.min_move_pct = min_move_pct

        # Rolling price history: symbol -> deque of (timestamp, price)
        self._history: dict[str, deque] = {
            s: deque(maxlen=5000) for s in self.symbols
        }
        self._latest: dict[str, PriceTick] = {}
        self._signal_callbacks: list[Callable[[MomentumSignal], None]] = []
        self._running = False
        self._ws_url = "wss://stream.binance.com:9443/ws"

    def on_signal(self, callback: Callable[[MomentumSignal], None]) -> None:
        self._signal_callbacks.append(callback)

    def get_latest(self, symbol: str) -> Optional[PriceTick]:
        return self._latest.get(symbol.lower())

    def get_price_change_pct(self, symbol: str, window_secs: int) -> Optional[float]:
        """Returns % price change over the last N seconds. Positive = up."""
        sym = symbol.lower()
        history = self._history.get(sym)
        if not history or len(history) < 2:
            return None

        now = time.time()
        cutoff = now - window_secs
        old_price = None
        current_price = history[-1][1]

        for ts, price in reversed(history):
            if ts <= cutoff:
                old_price = price
                break

        if old_price is None or old_price == 0:
            return None

        return (current_price - old_price) / old_price

    async def _connect(self) -> None:
        streams = "/".join(f"{s}@bookTicker" for s in self.symbols)
        url = f"{self._ws_url}/{streams}"

        logger.info(f"Connecting to Binance feed: {url}")

        async with websockets.connect(
            url,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=5,
        ) as ws:
            self._running = True
            logger.info("Binance WebSocket connected")
            async for raw in ws:
                if not self._running:
                    break
                try:
                    await self._handle_message(raw)
                except Exception as e:
                    logger.warning(f"Error processing message: {e}")

    async def _handle_message(self, raw: str) -> None:
        data = json.loads(raw)

        # bookTicker payload: {"s": "BTCUSDT", "b": bid, "a": ask, ...}
        symbol = data.get("s", "").lower()
        if symbol not in self.symbols:
            return

        bid = float(data.get("b", 0))
        ask = float(data.get("a", 0))
        mid_price = (bid + ask) / 2 if bid and ask else 0.0

        if mid_price == 0:
            return

        now = time.time()
        tick = PriceTick(
            symbol=symbol,
            price=mid_price,
            timestamp=now,
            bid=bid,
            ask=ask,
        )
        self._latest[symbol] = tick
        self._history[symbol].append((now, mid_price))

        # Check for momentum signal
        await self._check_momentum(symbol, mid_price, now)

    async def _check_momentum(
        self, symbol: str, current_price: float, now: float
    ) -> None:
        change_pct = self.get_price_change_pct(symbol, self.momentum_window_secs)
        if change_pct is None:
            return

        if abs(change_pct) < self.min_move_pct:
            return

        # Measure consistency: count ticks moving in same direction
        history = list(self._history[symbol])
        cutoff = now - self.momentum_window_secs
        window_ticks = [(ts, p) for ts, p in history if ts >= cutoff]

        if len(window_ticks) < 3:
            return

        direction = "UP" if change_pct > 0 else "DOWN"
        consistent_moves = sum(
            1
            for i in range(1, len(window_ticks))
            if (window_ticks[i][1] > window_ticks[i - 1][1]) == (change_pct > 0)
        )
        confidence = consistent_moves / (len(window_ticks) - 1)

        signal = MomentumSignal(
            symbol=symbol,
            direction=direction,
            magnitude_pct=abs(change_pct),
            duration_secs=now - window_ticks[0][0],
            current_price=current_price,
            start_price=window_ticks[0][1],
            confidence=confidence,
        )

        for cb in self._signal_callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(signal)
                else:
                    cb(signal)
            except Exception as e:
                logger.error(f"Signal callback error: {e}")

    async def run(self) -> None:
        """Run with automatic reconnection on disconnect."""
        backoff = 1
        while True:
            try:
                await self._connect()
            except Exception as e:
                logger.warning(f"Binance feed disconnected: {e}. Reconnecting in {backoff}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
            else:
                backoff = 1

    def stop(self) -> None:
        self._running = False
