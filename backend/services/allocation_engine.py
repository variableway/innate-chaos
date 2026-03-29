"""Allocation engine for portfolio weight calculation."""

import logging
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from models.allocation import Allocation
from services.risk_classifier import Regime

logger = logging.getLogger(__name__)


class AllocationEngine:
    """Calculate portfolio allocation based on signals and regime."""
    
    def __init__(self):
        self.rebalance_threshold = settings.REBALANCE_THRESHOLD
    
    def calculate_weights(self, eth_signal: float, btc_signal: float,
                         gold_signal: float, regime: Regime,
                         macro_state: str = "TIGHT") -> Dict[str, float]:
        """
        Calculate portfolio weights.
        
        Args:
            eth_signal: ETH signal score (0-1)
            btc_signal: BTC signal score (0-1)
            gold_signal: GOLD signal score (0-1)
            regime: Current market regime
            macro_state: "TIGHT" or "EASING"
        
        Returns:
            Dict of asset -> weight
        """
        # Base weights from signals
        total_signal = eth_signal + btc_signal + gold_signal
        
        if total_signal == 0:
            # All signals zero - go to cash
            return {"ETH": 0.0, "BTC": 0.0, "GOLD": 0.0, "CASH": 1.0}
        
        weights = {
            "ETH": eth_signal / total_signal,
            "BTC": btc_signal / total_signal,
            "GOLD": gold_signal / total_signal
        }
        
        # Apply macro filter
        if macro_state == "TIGHT":
            weights["ETH"] *= 0.7  # Reduce ETH in tight conditions
            weights["BTC"] *= 0.9
            weights["GOLD"] *= 1.1
        elif macro_state == "EASING":
            weights["ETH"] *= 1.2  # Increase ETH in easing
            weights["BTC"] *= 1.1
            weights["GOLD"] *= 0.9
        
        # Re-normalize
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        # Reserve 30% cash buffer
        weights = {k: v * 0.7 for k, v in weights.items()}
        weights["CASH"] = 0.3
        
        return weights
    
    def get_regime_based_allocation(self, regime: Regime) -> Dict[str, float]:
        """
        Get allocation based purely on regime (fallback method).
        
        Risk-On: BTC 60%, GOLD 10%, CASH 30%
        Neutral: BTC 40%, GOLD 30%, CASH 30%
        Risk-Off: BTC 20%, GOLD 50%, CASH 30%
        """
        allocations = {
            Regime.RISK_ON: {"ETH": 0.35, "BTC": 0.25, "GOLD": 0.10, "CASH": 0.30},
            Regime.NEUTRAL: {"ETH": 0.25, "BTC": 0.20, "GOLD": 0.25, "CASH": 0.30},
            Regime.RISK_OFF: {"ETH": 0.15, "BTC": 0.15, "GOLD": 0.40, "CASH": 0.30}
        }
        
        return allocations.get(regime, allocations[Regime.NEUTRAL])
    
    def should_rebalance(self, current: Dict[str, float], 
                        target: Dict[str, float]) -> tuple[bool, list]:
        """
        Check if rebalancing is needed.
        
        Returns:
            Tuple of (should_rebalance, list of assets exceeding threshold)
        """
        exceeded = []
        
        all_assets = set(current.keys()) | set(target.keys())
        
        for asset in all_assets:
            current_weight = current.get(asset, 0)
            target_weight = target.get(asset, 0)
            
            if abs(target_weight - current_weight) > self.rebalance_threshold:
                exceeded.append(asset)
        
        return len(exceeded) > 0, exceeded
    
    async def get_current_allocation(self, db: AsyncSession) -> Optional[Allocation]:
        """Get the most recent allocation."""
        query = select(Allocation).order_by(desc(Allocation.created_at)).limit(1)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def calculate_and_save(self, db: AsyncSession, 
                                  signals: Dict[str, float],
                                  regime: Regime,
                                  macro_state: str = "TIGHT") -> Allocation:
        """
        Calculate new allocation and save if needed.
        
        Args:
            db: Database session
            signals: Dict of asset -> signal score
            regime: Current market regime
            macro_state: "TIGHT" or "EASING"
        
        Returns:
            New Allocation object
        """
        # Calculate new weights
        new_weights = self.calculate_weights(
            signals.get("ETH", 0.5),
            signals.get("BTC", 0.5),
            signals.get("GOLD", 0.5),
            regime,
            macro_state
        )
        
        # Check if rebalancing needed
        current_alloc = await self.get_current_allocation(db)
        rebalance_needed = False
        
        if current_alloc:
            current_weights = {
                "ETH": current_alloc.eth_weight,
                "BTC": current_alloc.btc_weight,
                "GOLD": current_alloc.gold_weight,
                "CASH": current_alloc.cash_weight
            }
            rebalance_needed, _ = self.should_rebalance(current_weights, new_weights)
        else:
            rebalance_needed = True  # First allocation
        
        # Create new allocation record
        allocation = Allocation(
            eth_weight=new_weights["ETH"],
            btc_weight=new_weights["BTC"],
            gold_weight=new_weights["GOLD"],
            cash_weight=new_weights["CASH"],
            regime=regime.value,
            macro_state=macro_state,
            rebalance_triggered=rebalance_needed
        )
        
        db.add(allocation)
        await db.commit()
        
        logger.info(f"Created allocation: ETH={allocation.eth_weight:.2%}, "
                   f"BTC={allocation.btc_weight:.2%}, "
                   f"GOLD={allocation.gold_weight:.2%}, "
                   f"CASH={allocation.cash_weight:.2%}, "
                   f"rebalance={rebalance_needed}")
        
        return allocation
    
    def get_allocation_rationale(self, regime: Regime, 
                                  weights: Dict[str, float]) -> str:
        """Generate explanation for allocation."""
        primary = max(weights, key=weights.get)
        
        rationales = {
            Regime.RISK_OFF: (
                f"Oil spike detected - defensive positioning. "
                f"Increasing {primary} to {weights[primary]:.0%} for protection."
            ),
            Regime.RISK_ON: (
                f"Risk-on conditions favorable. "
                f"{primary} allocation at {weights[primary]:.0%} to capture upside."
            ),
            Regime.NEUTRAL: (
                f"Neutral conditions - balanced approach. "
                f"Maintaining {weights[primary]:.0%} in {primary}."
            )
        }
        
        return rationales.get(regime, "Standard allocation")
