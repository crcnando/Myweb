"""
Polymarket CLOB API Client (wraps py-clob-client).
Handles market discovery, order book reading, and order execution.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Market:
    condition_id: str
    question: str
    end_time: float        # Unix timestamp
    yes_token_id: str
    no_token_id: str
    yes_price: float       # Current YES price (0.0 - 1.0)
    no_price: float        # Current NO price
    volume: float          # Total volume in USDC
    active: bool


@dataclass
class OrderResult:
    success: bool
    order_id: Optional[str]
    filled_price: Optional[float]
    filled_size: Optional[float]
    error: Optional[str] = None
    latency_ms: Optional[float] = None


class PolymarketClient:
    """
    Thin wrapper around py-clob-client.
    Install: pip install py-clob-client
    """

    def __init__(self, config):
        self.config = config
        self._client = None
        self._initialized = False

    def initialize(self) -> bool:
        """Connect to CLOB and set up credentials."""
        try:
            from py_clob_client.client import ClobClient
            from py_clob_client.clob_types import ApiCreds

            creds = ApiCreds(
                api_key=self.config.POLY_API_KEY,
                api_secret=self.config.POLY_API_SECRET,
                api_passphrase=self.config.POLY_API_PASSPHRASE,
            )
            self._client = ClobClient(
                host=self.config.POLY_HOST,
                chain_id=self.config.POLY_CHAIN_ID,
                key=self.config.POLY_PRIVATE_KEY,
                creds=creds,
            )
            self._initialized = True
            logger.info("Polymarket CLOB client initialized")
            return True
        except ImportError:
            logger.error("py-clob-client not installed. Run: pip install py-clob-client")
            return False
        except Exception as e:
            logger.error(f"Polymarket init failed: {e}")
            return False

    def get_active_crypto_markets(
        self,
        symbol: str = "BTC",
        max_duration_mins: int = 20,
    ) -> list[Market]:
        """Fetch short-duration crypto markets for the given symbol."""
        if not self._initialized:
            return []

        try:
            import requests

            now = time.time()
            url = f"{self.config.POLY_GAMMA_HOST}/markets"
            params = {
                "active": True,
                "closed": False,
                "limit": 100,
                "tag": "crypto",
            }
            resp = requests.get(url, params=params, timeout=5)
            resp.raise_for_status()
            raw_markets = resp.json()

            markets = []
            for m in raw_markets:
                question = m.get("question", "").lower()
                if symbol.lower() not in question:
                    continue

                end_time = m.get("endDate", 0)
                if isinstance(end_time, str):
                    from datetime import datetime
                    end_time = datetime.fromisoformat(
                        end_time.replace("Z", "+00:00")
                    ).timestamp()

                time_remaining = end_time - now
                if time_remaining <= 0:
                    continue
                if time_remaining > max_duration_mins * 60:
                    continue

                tokens = m.get("tokens", [])
                yes_token = next((t for t in tokens if t.get("outcome") == "Yes"), None)
                no_token = next((t for t in tokens if t.get("outcome") == "No"), None)

                if not yes_token or not no_token:
                    continue

                yes_price = float(yes_token.get("price", 0.5))
                no_price = float(no_token.get("price", 0.5))

                markets.append(Market(
                    condition_id=m.get("conditionId", ""),
                    question=m.get("question", ""),
                    end_time=end_time,
                    yes_token_id=yes_token.get("token_id", ""),
                    no_token_id=no_token.get("token_id", ""),
                    yes_price=yes_price,
                    no_price=no_price,
                    volume=float(m.get("volume", 0)),
                    active=True,
                ))

            return sorted(markets, key=lambda m: m.end_time)

        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []

    def place_market_order(
        self,
        token_id: str,
        side: str,           # "BUY" or "SELL"
        size_usdc: float,
        price: float,        # Limit price (0.0 - 1.0)
        paper: bool = True,
    ) -> OrderResult:
        """Place a limit order on the CLOB."""
        start = time.time()

        if paper:
            latency = (time.time() - start) * 1000
            logger.info(f"[PAPER] {side} {size_usdc:.2f} USDC @ {price:.3f} | token={token_id[:8]}...")
            return OrderResult(
                success=True,
                order_id=f"paper_{int(time.time()*1000)}",
                filled_price=price,
                filled_size=size_usdc / price,
                latency_ms=latency,
            )

        if not self._initialized:
            return OrderResult(success=False, order_id=None, filled_price=None,
                               filled_size=None, error="Client not initialized")

        try:
            from py_clob_client.clob_types import OrderArgs, OrderType

            order_args = OrderArgs(
                token_id=token_id,
                price=round(price, 4),
                size=round(size_usdc / price, 2),
                side=side,
            )
            resp = self._client.create_and_post_order(order_args)
            latency_ms = (time.time() - start) * 1000

            logger.info(
                f"Order placed: {side} {size_usdc:.2f} USDC @ {price:.3f} "
                f"| id={resp.get('orderID', '?')} | {latency_ms:.0f}ms"
            )

            return OrderResult(
                success=True,
                order_id=resp.get("orderID"),
                filled_price=float(resp.get("price", price)),
                filled_size=float(resp.get("size", 0)),
                latency_ms=latency_ms,
            )

        except Exception as e:
            return OrderResult(
                success=False,
                order_id=None,
                filled_price=None,
                filled_size=None,
                error=str(e),
            )

    def cancel_order(self, order_id: str) -> bool:
        if not self._initialized or not order_id:
            return False
        try:
            self._client.cancel(order_id)
            return True
        except Exception as e:
            logger.warning(f"Cancel order {order_id} failed: {e}")
            return False

    def get_balance(self) -> float:
        """Returns available USDC balance."""
        if not self._initialized:
            return 0.0
        try:
            balances = self._client.get_balance()
            return float(balances.get("USDC", 0))
        except Exception as e:
            logger.error(f"Balance fetch error: {e}")
            return 0.0
