"""Price model for storing asset prices - TimescaleDB hypertable."""

from datetime import datetime
from sqlalchemy import Column, String, Float, Index, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.database import Base


class Price(Base):
    """
    Price model for asset prices.
    
    This table is converted to a TimescaleDB hypertable on initialization
    for optimal time-series storage and querying.
    
    Hypertable configuration:
    - Partition column: time
    - Chunk interval: 7 days
    - Compression: Enabled (segmented by asset)
    - Retention: 90 days
    """
    
    __tablename__ = "prices"
    
    # Primary key is composite: (time, asset) for TimescaleDB
    time = Column(TIMESTAMP(timezone=True), nullable=False)
    asset = Column(String(10), nullable=False)
    
    # Price data
    price = Column(Float, nullable=False)
    source = Column(String(50), nullable=False)
    
    # Price changes (optional, calculated)
    change_24h = Column(Float, nullable=True)
    change_7d = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    
    # Primary key constraint
    __table_args__ = (
        PrimaryKeyConstraint('time', 'asset'),
        Index('idx_prices_asset_time', 'asset', 'time DESC'),
        # TimescaleDB-specific: this table will be converted to hypertable
        {'timescaledb_hypertable': True}
    )
    
    def __repr__(self):
        return f"<Price(asset='{self.asset}', price={self.price}, time='{self.time}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "asset": self.asset,
            "price": self.price,
            "time": self.time.isoformat() if self.time else None,
            "source": self.source,
            "change_24h": self.change_24h,
            "change_7d": self.change_7d,
            "volume_24h": self.volume_24h
        }
