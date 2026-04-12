from datetime import datetime, timedelta, timezone

import httpx
import structlog

from app.adapters.base import BaseAdapter
from app.config import settings

logger = structlog.get_logger()

# FRED series ID -> friendly asset name
SERIES_MAP: dict[str, str] = {
    "DFF": "DFF",           # Federal Funds Effective Rate
    "DGS2": "DGS2",         # 2-Year Treasury
    "DGS5": "DGS5",         # 5-Year Treasury
    "DGS10": "DGS10",       # 10-Year Treasury
    "DGS20": "DGS20",       # 20-Year Treasury
    "DGS30": "DGS30",       # 30-Year Treasury
    "T10Y2Y": "T10Y2Y",     # 10Y-2Y Spread
    "GOLDAMGBD228NLBM": "GOLD",  # Gold (London AM Fix)
    "DCOILWTICO": "OIL",    # WTI Crude Oil
}

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


class FredAdapter(BaseAdapter):
    def __init__(self) -> None:
        self.api_key = settings.fred_api_key

    async def fetch_series(
        self, series_id: str, start_date: str | None = None, limit: int = 1
    ) -> list[dict]:
        """Fetch observations for a single FRED series."""
        if not self.api_key or self.api_key == "your_fred_api_key_here":
            logger.warning("fred_no_api_key")
            return []

        if not start_date:
            start_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit,
            "observation_start": start_date,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(FRED_BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

            observations = data.get("observations", [])
            results: list[dict] = []

            for obs in observations:
                raw_value = obs.get("value", ".")
                if raw_value == "." or raw_value is None:
                    continue
                try:
                    price = float(raw_value)
                except (ValueError, TypeError):
                    continue

                # Parse observation date into timezone-aware datetime
                obs_date = obs.get("date", "")
                try:
                    obs_time = datetime.strptime(obs_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue

                friendly_name = SERIES_MAP.get(series_id, series_id)
                results.append({
                    "time": obs_time,
                    "asset": friendly_name,
                    "price": price,
                    "source": "fred",
                    "change_24h": None,
                    "volume_24h": None,
                })

            return results

        except httpx.HTTPError as exc:
            logger.error("fred_http_error", series_id=series_id, error=str(exc))
            return []
        except Exception as exc:
            logger.error("fred_unexpected_error", series_id=series_id, error=str(exc))
            return []

    async def fetch_latest(self) -> list[dict]:
        """Fetch latest data for all tracked FRED series."""
        results: list[dict] = []

        for series_id in SERIES_MAP:
            observations = await self.fetch_series(series_id)
            if observations:
                results.extend(observations)

        return results

    async def fetch_history(self, series_id: str, days: int = 30) -> list[dict]:
        """Fetch historical data for a single series."""
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        return await self.fetch_series(series_id, start_date=start_date, limit=days + 10)
