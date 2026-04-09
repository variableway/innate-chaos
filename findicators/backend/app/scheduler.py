import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.adapters.fred import FredAdapter
from app.adapters.hyperliquid import HyperLiquidAdapter
from app.adapters.yahoo_finance import YahooFinanceAdapter
from app.config import settings
from app.database import async_session
from app.services.price_service import PriceService
from app.services.risk_engine import RiskEngine

logger = structlog.get_logger()

scheduler = AsyncIOScheduler()


async def _fetch_crypto() -> None:
    """Job: fetch crypto prices (BTC, ETH, PAXG/GOLD) and store in DB."""
    try:
        adapter = HyperLiquidAdapter()
        async with async_session() as db:
            service = PriceService(db, adapters=[adapter])
            await service.fetch_and_store()
        logger.info("crypto_fetch_complete")
    except Exception as exc:
        logger.error("crypto_fetch_job_error", error=str(exc))


async def _fetch_economic() -> None:
    """Job: fetch economic data (OIL, rates) from Yahoo Finance and FRED, store in DB."""
    try:
        adapters: list = [YahooFinanceAdapter()]
        # Only add FRED if API key is configured
        if settings.fred_api_key and settings.fred_api_key != "your_fred_api_key_here":
            adapters.append(FredAdapter())

        async with async_session() as db:
            service = PriceService(db, adapters=adapters)
            await service.fetch_and_store()
        logger.info("economic_fetch_complete")
    except Exception as exc:
        logger.error("economic_fetch_job_error", error=str(exc))


async def _calculate_risk() -> None:
    """Job: calculate risk score and persist regime."""
    try:
        async with async_session() as db:
            engine = RiskEngine(db)
            await engine.assess()
        logger.info("risk_assessment_complete")
    except Exception as exc:
        logger.error("risk_assessment_job_error", error=str(exc))


async def _backfill_history() -> None:
    """One-time job: backfill historical data from all sources."""
    try:
        async with async_session() as db:
            service = PriceService(db, adapters=[])

            # 1. HyperLiquid candle history (BTC, ETH, PAXG/GOLD)
            hl_adapter = HyperLiquidAdapter()
            for coin in ["BTC", "ETH", "PAXG"]:
                candles = await hl_adapter.fetch_candles(coin, interval="1d", days=30)
                if candles:
                    count = await service.store_history(candles)
                    logger.info("backfill_hl", coin=coin, inserted=count)

            # 2. Yahoo Finance history (OIL, rates)
            yahoo = YahooFinanceAdapter()
            for symbol, friendly in YahooFinanceAdapter.SYMBOL_MAP.items():
                history = await yahoo.fetch_history(symbol, friendly, days=30)
                if history:
                    count = await service.store_history(history)
                    logger.info("backfill_yahoo", symbol=friendly, inserted=count)

            # 3. FRED history (if key configured)
            if settings.fred_api_key and settings.fred_api_key != "your_fred_api_key_here":
                fred = FredAdapter()
                for series_id, friendly in FredAdapter.SERIES_MAP.items():
                    history = await fred.fetch_history(series_id, days=30)
                    if history:
                        count = await service.store_history(history)
                        logger.info("backfill_fred", series=friendly, inserted=count)

        logger.info("backfill_complete")
    except Exception as exc:
        logger.error("backfill_error", error=str(exc))


def start() -> None:
    """Configure and start the scheduler."""
    # Backfill historical data on startup
    scheduler.add_job(
        _backfill_history,
        "date",
        id="backfill_history",
        replace_existing=True,
    )

    # Crypto prices every 5 minutes
    scheduler.add_job(
        _fetch_crypto,
        "interval",
        seconds=settings.crypto_fetch_interval_seconds,
        id="fetch_crypto",
        replace_existing=True,
    )

    # Economic data every 24 hours
    scheduler.add_job(
        _fetch_economic,
        "interval",
        seconds=settings.economic_fetch_interval_seconds,
        id="fetch_economic",
        replace_existing=True,
    )

    # Risk score calculation every 5 minutes
    scheduler.add_job(
        _calculate_risk,
        "interval",
        seconds=settings.crypto_fetch_interval_seconds,
        id="calculate_risk",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("scheduler_started")


def shutdown() -> None:
    """Gracefully shut down the scheduler."""
    scheduler.shutdown(wait=False)
    logger.info("scheduler_stopped")
