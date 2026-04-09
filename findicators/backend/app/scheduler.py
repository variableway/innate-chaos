import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.fred import FredAdapter
from app.adapters.hyperliquid import HyperLiquidAdapter
from app.config import settings
from app.database import async_session
from app.services.price_service import PriceService
from app.services.risk_engine import RiskEngine

logger = structlog.get_logger()

scheduler = AsyncIOScheduler()


async def _fetch_crypto() -> None:
    """Job: fetch crypto prices and store in DB."""
    try:
        adapter = HyperLiquidAdapter()
        async with async_session() as db:
            service = PriceService(db, adapters=[adapter])
            await service.fetch_and_store()
        logger.info("crypto_fetch_complete")
    except Exception as exc:
        logger.error("crypto_fetch_job_error", error=str(exc))


async def _fetch_economic() -> None:
    """Job: fetch FRED economic data and store in DB."""
    try:
        adapter = FredAdapter()
        async with async_session() as db:
            service = PriceService(db, adapters=[adapter])
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


def start() -> None:
    """Configure and start the scheduler."""
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
