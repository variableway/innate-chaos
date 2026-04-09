from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Price(Base):
    __tablename__ = "prices"

    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, default=lambda: datetime.now(timezone.utc)
    )
    asset: Mapped[str] = mapped_column(String(10), primary_key=True)
    price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    change_24h: Mapped[float | None] = mapped_column(Numeric(10, 4))
    volume_24h: Mapped[float | None] = mapped_column(Numeric(20, 4))

    __table_args__ = (
        Index("ix_prices_asset_time", "asset", "time"),
    )
