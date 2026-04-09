import time
from datetime import datetime, timezone

import httpx
import structlog

from app.adapters.base import BaseAdapter
from app.config import settings

logger = structlog.get_logger()

# HyperLiquid perpetual symbols to track
SYMBOLS = {
    "BTC": "BTC",
    "ETH": "ETH",
    "GOLD": "PAXG",  # PAXG = Paxos Gold, tracks physical gold price (1 PAXG ≈ 1 oz gold)
}


class HyperLiquidAdapter(BaseAdapter):
    def __init__(self) -> None:
        self.api_url = settings.hyperliquid_api_url

    async def fetch_latest(self) -> list[dict]:
        """Fetch BTC, ETH, and PAXG (gold proxy) mid prices with 24h change and volume."""
        results: list[dict] = []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Fetch all mid prices
                mids_resp = await client.post(
                    f"{self.api_url}/info",
                    json={"type": "allMids"},
                )
                mids_resp.raise_for_status()
                mids_data = mids_resp.json()

                # Fetch perpetual meta and asset contexts
                ctx_resp = await client.post(
                    f"{self.api_url}/info",
                    json={"type": "metaAndAssetCtxs"},
                )
                ctx_resp.raise_for_status()
                ctx_data = ctx_resp.json()

            # ctx_data is [meta, asset_ctxs] where meta has "universe" list
            meta = ctx_data[0] if isinstance(ctx_data, list) and len(ctx_data) >= 2 else {}
            asset_ctxs = ctx_data[1] if isinstance(ctx_data, list) and len(ctx_data) >= 2 else []

            universe = meta.get("universe", []) if isinstance(meta, dict) else []

            # Build lookup: symbol -> asset context
            ctx_lookup: dict[str, dict] = {}
            for idx, ctx in enumerate(asset_ctxs):
                if idx < len(universe):
                    symbol = universe[idx].get("name", "")
                    ctx_lookup[symbol] = ctx

            for friendly_name, symbol in SYMBOLS.items():
                try:
                    price = float(mids_data.get(symbol, 0))
                    if price == 0:
                        logger.warning("hyperliquid_zero_price", symbol=symbol)
                        continue

                    ctx = ctx_lookup.get(symbol, {})
                    prev_day_px = float(ctx.get("prevDayPx", 0))
                    day_ntl_vlm = float(ctx.get("dayNtlVlm", 0))

                    change_24h = 0.0
                    if prev_day_px > 0:
                        change_24h = (price - prev_day_px) / prev_day_px

                    results.append({
                        "asset": friendly_name,
                        "price": price,
                        "source": "hyperliquid",
                        "change_24h": change_24h,
                        "volume_24h": day_ntl_vlm,
                    })
                except (ValueError, TypeError, KeyError) as exc:
                    logger.warning("hyperliquid_parse_error", symbol=symbol, error=str(exc))
                    continue

        except httpx.HTTPError as exc:
            logger.error("hyperliquid_http_error", error=str(exc))
        except Exception as exc:
            logger.error("hyperliquid_unexpected_error", error=str(exc))

        return results

    async def fetch_candles(
        self, coin: str, interval: str = "1d", days: int = 30
    ) -> list[dict]:
        """Fetch historical candle data from HyperLiquid.

        Returns list of dicts with keys: time (datetime), asset, price, source, volume_24h.
        """
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - (days * 24 * 60 * 60 * 1000)

        results: list[dict] = []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_url}/info",
                    json={
                        "type": "candleSnapshot",
                        "req": {
                            "coin": coin,
                            "interval": interval,
                            "startTime": start_ms,
                        },
                    },
                )
                resp.raise_for_status()
                candles = resp.json()

            friendly_name = SYMBOLS.get(coin, coin)

            for c in candles:
                try:
                    ts = datetime.fromtimestamp(c["t"] / 1000, tz=timezone.utc)
                    close_price = float(c["c"])
                    volume = float(c.get("v", 0))

                    results.append({
                        "time": ts,
                        "asset": friendly_name,
                        "price": close_price,
                        "source": "hyperliquid",
                        "change_24h": None,
                        "volume_24h": volume,
                    })
                except (ValueError, TypeError, KeyError) as exc:
                    logger.warning("hyperliquid_candle_parse_error", error=str(exc))
                    continue

        except httpx.HTTPError as exc:
            logger.error("hyperliquid_candle_http_error", coin=coin, error=str(exc))
        except Exception as exc:
            logger.error("hyperliquid_candle_error", coin=coin, error=str(exc))

        return results
