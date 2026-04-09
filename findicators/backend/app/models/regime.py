from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RegimeHistory(Base):
    __tablename__ = "regime_history"

    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, default=lambda: datetime.now(timezone.utc)
    )
    regime: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    factor_scores: Mapped[dict | None] = mapped_column(JSONB)
    description: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        Index("ix_regime_time", "time"),
    )
