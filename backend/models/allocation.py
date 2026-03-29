"""Allocation model for portfolio weights."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index
from app.database import Base


class Allocation(Base):
    """Allocation model for portfolio weights."""
    
    __tablename__ = "allocations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Weights (should sum to 1.0)
    eth_weight = Column(Float, nullable=False)
    btc_weight = Column(Float, nullable=False)
    gold_weight = Column(Float, nullable=False)
    cash_weight = Column(Float, nullable=False)
    
    # Market conditions
    regime = Column(String(20), nullable=False)
    macro_state = Column(String(10), default="TIGHT")
    
    # Whether rebalance was triggered
    rebalance_triggered = Column(Boolean, default=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_allocation_time', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Allocation(regime='{self.regime}', eth={self.eth_weight}, btc={self.btc_weight}, gold={self.gold_weight})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "weights": {
                "ETH": self.eth_weight,
                "BTC": self.btc_weight,
                "GOLD": self.gold_weight,
                "CASH": self.cash_weight
            },
            "regime": self.regime,
            "macro_state": self.macro_state,
            "rebalance_triggered": self.rebalance_triggered
        }
    
    def get_primary_asset(self):
        """Get the asset with highest weight."""
        weights = {
            "ETH": self.eth_weight,
            "BTC": self.btc_weight,
            "GOLD": self.gold_weight
        }
        return max(weights, key=weights.get)
