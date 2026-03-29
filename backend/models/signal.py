"""Signal model for trading signals - TimescaleDB hypertable."""

from datetime import datetime
from sqlalchemy import Column, String, Float, Index, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.database import Base
from app.config import settings


class Signal(Base):
    """
    Signal model for trading signals.
    
    This table is converted to a TimescaleDB hypertable on initialization.
    
    Hypertable configuration:
    - Partition column: time
    - Chunk interval: 7 days
    - Retention: 365 days (signals are valuable for backtesting)
    """
    
    __tablename__ = "signals"
    
    # Primary key is composite: (time, asset) for TimescaleDB
    time = Column(TIMESTAMP(timezone=True), nullable=False)
    asset = Column(String(10), nullable=False)
    
    # Signal value (0.0 to 1.0)
    signal_value = Column(Float, nullable=False)
    
    # Score breakdown
    policy_score = Column(Float, nullable=True)
    momentum_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    
    # Market regime when signal was calculated
    regime = Column(String(20), nullable=False)
    
    # Primary key constraint
    __table_args__ = (
        PrimaryKeyConstraint('time', 'asset'),
        Index('idx_signals_asset_time', 'asset', 'time DESC'),
        {'timescaledb_hypertable': True}
    )
    
    def __repr__(self):
        return f"<Signal(asset='{self.asset}', signal={self.signal_value}, regime='{self.regime}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "asset": self.asset,
            "signal": self.signal_value,
            "score_breakdown": {
                "policy": self.policy_score,
                "momentum": self.momentum_score,
                "risk": self.risk_score
            },
            "regime": self.regime,
            "time": self.time.isoformat() if self.time else None
        }
    
    def get_action(self, thresholds: dict = None):
        """Get action based on signal value."""
        if thresholds is None:
            thresholds = settings.SIGNAL_THRESHOLDS
        
        if self.signal_value >= thresholds.get("STRONG", 0.7):
            return "STRONG"
        elif self.signal_value >= thresholds.get("MODERATE", 0.5):
            return "MODERATE"
        elif self.signal_value >= thresholds.get("WEAK", 0.3):
            return "WEAK"
        else:
            return "AVOID"
    
    def get_action_text(self):
        """Get human-readable action text."""
        action = self.get_action()
        action_map = {
            "STRONG": "🔥 Strong Trend: Heavy position",
            "MODERATE": "🟢 Early Trend: Add position",
            "WEAK": "🟡 Watch: Small position",
            "AVOID": "🔴 Avoid"
        }
        return action_map.get(action, "Unknown")
