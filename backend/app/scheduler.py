"""Background task scheduler for data fetching and signal calculation."""

import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal
from services.data_fetcher import DataFetcher
from services.signal_engine import SignalEngine
from services.risk_classifier import RiskClassifier
from services.allocation_engine import AllocationEngine

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


def start_scheduler():
    """Start the background scheduler."""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running")
        return
    
    scheduler = AsyncIOScheduler()
    
    # Add jobs
    scheduler.add_job(
        fetch_prices_job,
        trigger=IntervalTrigger(minutes=settings.FETCH_INTERVAL_MINUTES),
        id="fetch_prices",
        name="Fetch prices from HyperLiquid",
        replace_existing=True
    )
    
    scheduler.add_job(
        calculate_signals_job,
        trigger=IntervalTrigger(minutes=settings.FETCH_INTERVAL_MINUTES),
        id="calculate_signals",
        name="Calculate trading signals",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"Scheduler started with {settings.FETCH_INTERVAL_MINUTES}min interval")


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler stopped")


async def fetch_prices_job():
    """Background job to fetch prices."""
    logger.info("Running fetch_prices job...")
    
    async with AsyncSessionLocal() as db:
        try:
            fetcher = DataFetcher()
            
            # Fetch all prices
            prices = await fetcher.fetch_all_prices()
            
            if prices:
                # Save to database
                await fetcher.save_prices(db, prices)
                logger.info(f"Fetched and saved {len(prices)} prices")
            else:
                logger.warning("No prices fetched")
            
            await fetcher.close()
            
        except Exception as e:
            logger.error(f"Error in fetch_prices job: {e}")
            await db.rollback()


async def calculate_signals_job():
    """Background job to calculate signals."""
    logger.info("Running calculate_signals job...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Get current regime
            classifier = RiskClassifier()
            regime_data = await classifier.get_current_regime(db)
            regime = classifier.classify(
                regime_data["oil_change_24h"],
                regime_data["gold_change_24h"]
            )
            
            # Calculate signals
            engine = SignalEngine()
            signals = await engine.calculate_all_signals(
                db,
                regime.value,
                regime_data["oil_change_24h"],
                regime_data["gold_change_24h"]
            )
            
            if signals:
                # Save signals
                await engine.save_signals(db, signals)
                logger.info(f"Calculated and saved {len(signals)} signals")
                
                # Update allocation
                signal_values = {asset: s.signal_value for asset, s in signals.items()}
                alloc_engine = AllocationEngine()
                await alloc_engine.calculate_and_save(
                    db, signal_values, regime, "TIGHT"
                )
                logger.info("Updated allocation")
            else:
                logger.warning("No signals calculated")
            
        except Exception as e:
            logger.error(f"Error in calculate_signals job: {e}")
            await db.rollback()


# Helper functions for manual triggering
async def run_fetch_prices():
    """Manually trigger price fetching."""
    await fetch_prices_job()


async def run_calculate_signals():
    """Manually trigger signal calculation."""
    await calculate_signals_job()
