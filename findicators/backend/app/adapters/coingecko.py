"""CoinGecko adapter for crypto and gold prices.

Fallback data source for BTC, ETH, and PAXG (gold proxy).
Free tier: ~30 calls/minute, no API key needed.
"""

from datetime import datetime, timezone

import httpx
import structlog

from app.adapters.base import BaseAdapter

logger = structlog.get_logger()

# CoinGecko ID -> friendly asset name
COIN_MAP = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "pax-gold": "GOLD",
}

COINGECKO_URL = "https://api.coingecko.com/api/v3"


class CoinGeckoAdapter(BaseAdapter):
    """Fetches BTC, ETH, and GOLD (PAXG) prices from CoinGecko."""

    def __init__(self) -> None:
        pass

    async def fetch_latest(self) -> list[dict]:
        """Fetch latest prices from CoinGecko simple/price endpoint."""
        ids = ",".join(COIN_MAP.keys())
        params = {
            "ids": ids,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
        }
        headers = {"Accept": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{COINGECKO_URL}/simple/price",
                    params=params,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()

            results: list[dict] = []
            for coin_id, friendly_name in COIN_MAP.items():
                coin_data = data.get(coin_id)
                if not coin_data:
                    continue

                price = coin_data.get("usd")
                if price is None:
                    continue

                change_24h = coin_data.get("usd_24h_change")
                volume_24h = coin_data.get("usd_24h_vol")

                results.append({
                    "asset": friendly_name,
                    "price": float(price),
                    "source": "coingecko",
                    "change_24h": float(change_24h / 100) if change_24h else None,
                    "volume_24h": float(volume_24h) if volume_24h else None,
                })

            return results

        except httpx.HTTPError as exc:
            logger.warning("coingecko_http_error", error=str(exc))
        except Exception as exc:
            logger.warning("coingecko_unexpected_error", error=str(exc))

        return []

    async def fetch_history(self, coin_id: str, days: int = 30) -> list[dict]:
        """Fetch historical market data from CoinGecko."""
        friendly_name = COIN_MAP.get(coin_id, coin_id)
        params = {
            "vs_currency": "usd",
            "days": str(days),
            "interval": "daily",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{COINGECKO_URL}/coins/{coin_id}/market_chart",
                    params=params,
                )
                resp.raise_for_status()
                data = resp.json()

            results: list[dict] = []
            for ts_ms, price in data.get("prices", []):
                dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
                results.append({
                    "time": dt,
                    "asset": friendly_name,
                    "price": float(price),
                    "source": "coingecko",
                    "change_24h": None,
                    "volume_24h": None,
                })

            return results

        except Exception as exc:
            logger.warning("coingecko_history_error", coin_id=coin_id, error=str(exc))
            return []
