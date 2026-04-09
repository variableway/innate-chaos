"""Yahoo Finance adapter for OIL and interest rate data.

Fetches commodity and economic data from Yahoo Finance API.
No API key required.
"""

import time
from datetime import datetime, timezone

import httpx
import structlog

from app.adapters.base import BaseAdapter

logger = structlog.get_logger()

# Yahoo Finance symbol -> friendly asset name
SYMBOL_MAP = {
    "CL=F": "OIL",        # WTI Crude Oil Futures
    "BZ=F": "BRENTOIL",   # Brent Crude Oil Futures
    "^TNX": "DGS10",      # 10-Year Treasury Yield
    "^TYX": "DGS30",      # 30-Year Treasury Yield
    "^FVX": "DGS5",       # 5-Year Treasury Yield
    "^IRX": "DGS13W",     # 13-Week Treasury (proxy for Fed Funds)
    "GC=F": "GOLD_YAHOO", # Gold Futures (backup for gold)
}

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart"


class YahooFinanceAdapter(BaseAdapter):
    """Fetches OIL, BRENTOIL, and interest rate data from Yahoo Finance."""

    def __init__(self) -> None:
        pass

    async def fetch_latest(self) -> list[dict]:
        """Fetch latest prices for all tracked Yahoo Finance symbols."""
        results: list[dict] = []

        for symbol, friendly_name in SYMBOL_MAP.items():
            try:
                data = await self._fetch_chart(symbol, range="5d", interval="1d")
                if not data:
                    continue

                result = self._parse_latest(data, friendly_name)
                if result:
                    results.append(result)
            except Exception as exc:
                logger.warning("yahoo_fetch_error", symbol=symbol, error=str(exc))
                continue

        return results

    async def _fetch_chart(
        self, symbol: str, range: str = "1mo", interval: str = "1d"
    ) -> dict | None:
        """Fetch chart data from Yahoo Finance."""
        params = {
            "symbol": symbol,
            "range": range,
            "interval": interval,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(YAHOO_CHART_URL, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            result = data.get("chart", {}).get("result", [])
            if result:
                return result[0]
        except httpx.HTTPError as exc:
            logger.warning("yahoo_http_error", symbol=symbol, error=str(exc))
        except Exception as exc:
            logger.warning("yahoo_unexpected_error", symbol=symbol, error=str(exc))

        return None

    def _parse_latest(self, data: dict, friendly_name: str) -> dict | None:
        """Parse latest price from Yahoo Finance chart response."""
        try:
            meta = data.get("meta", {})
            price = meta.get("regularMarketPrice")
            prev_price = meta.get("chartPreviousClose") or meta.get("previousClose")

            if price is None:
                return None

            change_24h = None
            if prev_price and prev_price > 0:
                change_24h = (price - prev_price) / prev_price

            return {
                "asset": friendly_name,
                "price": float(price),
                "source": "yahoo",
                "change_24h": change_24h,
                "volume_24h": None,
            }
        except Exception as exc:
            logger.warning("yahoo_parse_error", asset=friendly_name, error=str(exc))
            return None

    async def fetch_history(
        self, symbol: str, friendly_name: str, days: int = 30
    ) -> list[dict]:
        """Fetch historical daily data for a symbol."""
        data = await self._fetch_chart(symbol, range=f"{days}d", interval="1d")
        if not data:
            return []

        results: list[dict] = []
        timestamps = data.get("timestamp", [])
        quotes = data.get("indicators", {}).get("quote", [{}])
        closes = quotes[0].get("close", []) if quotes else []

        for i, ts in enumerate(timestamps):
            try:
                if i >= len(closes) or closes[i] is None:
                    continue
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                results.append({
                    "time": dt,
                    "asset": friendly_name,
                    "price": float(closes[i]),
                    "source": "yahoo",
                    "change_24h": None,
                    "volume_24h": None,
                })
            except Exception:
                continue

        return results
