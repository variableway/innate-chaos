from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Signal(Base):
    __tablename__ = "signals"

    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, default=lambda: datetime.now(timezone.utc)
    )
    asset: Mapped[str] = mapped_column(String(10), primary_key=True)
    signal_value: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB)
    action: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        Index("ix_signals_asset_time", "asset", "time"),
    )
