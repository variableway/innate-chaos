from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.base import BaseAdapter
from app.models.price import Price

logger = structlog.get_logger()


class PriceService:
    def __init__(self, db: AsyncSession, adapters: list[BaseAdapter]) -> None:
        self.db = db
        self.adapters = adapters

    async def fetch_and_store(self) -> None:
        """Call all adapters, deduplicate by (time, asset), and store to DB."""
        now = datetime.now(timezone.utc)

        for adapter in self.adapters:
            try:
                data_points = await adapter.fetch_latest()
            except Exception as exc:
                logger.error("adapter_fetch_error", adapter=adapter.__class__.__name__, error=str(exc))
                continue

            for point in data_points:
                try:
                    asset = point["asset"]
                    price = float(point["price"])
                    source = point["source"]
                    change_24h = point.get("change_24h")
                    volume_24h = point.get("volume_24h")

                    # Check for existing record at same time + asset
                    stmt = select(Price).where(
                        Price.time == now,
                        Price.asset == asset,
                    )
                    existing = (await self.db.execute(stmt)).scalar_one_or_none()

                    if existing is not None:
                        # Update in place rather than duplicate
                        existing.price = price
                        existing.source = source
                        existing.change_24h = change_24h
                        existing.volume_24h = volume_24h
                    else:
                        record = Price(
                            time=now,
                            asset=asset,
                            price=price,
                            source=source,
                            change_24h=change_24h,
                            volume_24h=volume_24h,
                        )
                        self.db.add(record)

                except Exception as exc:
                    logger.warning("price_store_error", asset=point.get("asset"), error=str(exc))
                    continue

            try:
                await self.db.commit()
            except Exception as exc:
                logger.error("price_commit_error", error=str(exc))
                await self.db.rollback()

    async def get_current_prices(self) -> list[Price]:
        """Return the latest price record for each asset."""
        # Subquery: latest time per asset
        from sqlalchemy import func

        subq = (
            select(Price.asset, func.max(Price.time).label("max_time"))
            .group_by(Price.asset)
            .subquery()
        )

        stmt = select(Price).join(
            subq,
            (Price.asset == subq.c.asset) & (Price.time == subq.c.max_time),
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_price_history(self, asset: str, days: int = 30) -> list[Price]:
        """Return price history for a given asset over the last N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(Price)
            .where(Price.asset == asset, Price.time >= cutoff)
            .order_by(Price.time.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
