"""Risk classifier for determining market regime."""

import logging
from enum import Enum
from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from models.price import Price

logger = logging.getLogger(__name__)


class Regime(Enum):
    """Market regime enum."""
    RISK_ON = "RISK_ON"
    RISK_OFF = "RISK_OFF"
    NEUTRAL = "NEUTRAL"
    
    def display_name(self) -> str:
        """Get display name."""
        return {
            Regime.RISK_ON: "Risk-On",
            Regime.RISK_OFF: "Risk-Off",
            Regime.NEUTRAL: "Neutral"
        }.get(self, "Unknown")
    
    def emoji(self) -> str:
        """Get emoji representation."""
        return {
            Regime.RISK_ON: "🟢",
            Regime.RISK_OFF: "🔴",
            Regime.NEUTRAL: "🟡"
        }.get(self, "⚪")
    
    def description(self) -> str:
        """Get regime description."""
        return {
            Regime.RISK_ON: "Favorable conditions for risk assets (BTC, ETH)",
            Regime.RISK_OFF: "Defensive conditions - favor GOLD and cash",
            Regime.NEUTRAL: "No clear directional bias"
        }.get(self, "Unknown regime")


class RiskClassifier:
    """Classify market regime based on OIL and GOLD."""
    
    def __init__(self):
        self.thresholds = settings.REGIME_THRESHOLDS
    
    def classify(self, oil_change: float, gold_change: float) -> Regime:
        """
        Classify market regime.
        
        Rules:
        - RISK_OFF: OIL > +5% AND GOLD > 0%
        - RISK_ON: OIL < -3% AND GOLD <= 0%
        - NEUTRAL: Everything else
        """
        # Risk-off conditions
        if oil_change > self.thresholds.get("RISK_OFF_OIL", 0.05) and gold_change > 0:
            return Regime.RISK_OFF
        
        # Risk-on conditions
        if oil_change < self.thresholds.get("RISK_ON_OIL", -0.03) and gold_change <= 0:
            return Regime.RISK_ON
        
        # Neutral
        return Regime.NEUTRAL
    
    def get_recommendation(self, regime: Regime) -> str:
        """Get recommendation text for regime."""
        recommendations = {
            Regime.RISK_OFF: "Increase GOLD position, reduce ETH/BTC exposure",
            Regime.RISK_ON: "Increase BTC/ETH exposure, reduce GOLD",
            Regime.NEUTRAL: "Maintain balanced allocation, wait for clarity"
        }
        return recommendations.get(regime, "No recommendation")
    
    async def get_current_changes(self, db: AsyncSession) -> Dict[str, float]:
        """Get current 24h changes for OIL and GOLD from TimescaleDB."""
        changes = {}
        
        for asset in ["OIL", "GOLD"]:
            # Try to get from latest price record
            query = select(Price).where(
                Price.asset == asset
            ).order_by(desc(Price.time)).limit(1)
            
            result = await db.execute(query)
            price = result.scalar_one_or_none()
            
            if price and price.change_24h is not None:
                changes[asset] = price.change_24h
            else:
                # Calculate from history
                cutoff = datetime.utcnow() - timedelta(hours=24)
                query = select(Price).where(
                    Price.asset == asset,
                    Price.time >= cutoff
                ).order_by(Price.time)
                
                result = await db.execute(query)
                prices = result.scalars().all()
                
                if len(prices) >= 2:
                    first = prices[0].price
                    last = prices[-1].price
                    changes[asset] = (last - first) / first if first > 0 else 0
                else:
                    changes[asset] = 0
        
        return changes
    
    async def get_current_regime(self, db: AsyncSession) -> Dict:
        """Get current regime with full details."""
        changes = await self.get_current_changes(db)
        
        oil_change = changes.get("OIL", 0)
        gold_change = changes.get("GOLD", 0)
        
        regime = self.classify(oil_change, gold_change)
        
        return {
            "regime": regime.value,
            "regime_text": regime.display_name(),
            "oil_change_24h": oil_change,
            "gold_change_24h": gold_change,
            "description": regime.description(),
            "recommendation": self.get_recommendation(regime),
            "time": datetime.utcnow().isoformat()
        }
