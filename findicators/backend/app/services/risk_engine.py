from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.regime import RegimeHistory
from app.services.signal_engine import SignalEngine

logger = structlog.get_logger()


class RiskEngine:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.signal_engine = SignalEngine(db)

    async def assess(self) -> dict:
        """Calculate risk score and persist the result in regime_history."""
        result = await self.signal_engine.calculate_risk_score()

        try:
            record = RegimeHistory(
                time=datetime.now(timezone.utc),
                regime=result["regime"],
                risk_score=result["risk_score"],
                factor_scores=result.get("factor_scores"),
                description=result.get("description"),
            )
            self.db.add(record)
            await self.db.commit()
        except Exception as exc:
            logger.error("regime_store_error", error=str(exc))
            await self.db.rollback()

        return result

    async def get_current_regime(self) -> RegimeHistory | None:
        """Return the latest regime record from DB."""
        stmt = select(RegimeHistory).order_by(RegimeHistory.time.desc()).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_regime_history(self, days: int = 30) -> list[RegimeHistory]:
        """Return regime history for the last N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(RegimeHistory)
            .where(RegimeHistory.time >= cutoff)
            .order_by(RegimeHistory.time.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
