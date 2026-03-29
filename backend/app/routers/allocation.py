"""Allocation API router."""

from typing import Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import settings
from models.allocation import Allocation
from services.allocation_engine import AllocationEngine
from services.risk_classifier import Regime

router = APIRouter(prefix="/allocation", tags=["allocation"])


@router.get("/current")
async def get_current_allocation(db: AsyncSession = Depends(get_db)):
    """Get current portfolio allocation."""
    query = select(Allocation).order_by(desc(Allocation.created_at)).limit(1)
    result = await db.execute(query)
    allocation = result.scalar_one_or_none()
    
    if not allocation:
        # Return default allocation
        default = {
            "time": datetime.utcnow().isoformat(),
            "regime": "NEUTRAL",
            "macro_state": "TIGHT",
            "weights": {
                "ETH": 0.25,
                "BTC": 0.20,
                "GOLD": 0.25,
                "CASH": 0.30
            },
            "rebalance_needed": True,
            "rationale": "Default allocation - insufficient data"
        }
        return {"success": True, "data": default}
    
    # Check if rebalance needed
    engine = AllocationEngine()
    rebalance_needed = False
    
    # Get second most recent for comparison
    query = select(Allocation).order_by(desc(Allocation.created_at)).offset(1).limit(1)
    result = await db.execute(query)
    prev_alloc = result.scalar_one_or_none()
    
    if prev_alloc:
        current_weights = {
            "ETH": allocation.eth_weight,
            "BTC": allocation.btc_weight,
            "GOLD": allocation.gold_weight,
            "CASH": allocation.cash_weight
        }
        prev_weights = {
            "ETH": prev_alloc.eth_weight,
            "BTC": prev_alloc.btc_weight,
            "GOLD": prev_alloc.gold_weight,
            "CASH": prev_alloc.cash_weight
        }
        rebalance_needed, _ = engine.should_rebalance(prev_weights, current_weights)
    
    data = allocation.to_dict()
    data["rebalance_needed"] = rebalance_needed or allocation.rebalance_triggered
    data["rationale"] = engine.get_allocation_rationale(
        Regime(allocation.regime), 
        data["weights"]
    )
    
    return {"success": True, "data": data}


@router.get("/history")
async def get_allocation_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get allocation history."""
    query = select(Allocation).order_by(desc(Allocation.created_at)).limit(limit)
    result = await db.execute(query)
    allocations = result.scalars().all()
    
    return {
        "success": True,
        "data": {
            "allocations": [a.to_dict() for a in allocations]
        }
    }


@router.post("/rebalance")
async def trigger_rebalance(db: AsyncSession = Depends(get_db)):
    """Manually trigger a rebalance calculation."""
    from services.signal_engine import SignalEngine
    from services.risk_classifier import RiskClassifier
    
    # Get current data
    classifier = RiskClassifier()
    regime_data = await classifier.get_current_regime(db)
    regime = Regime(regime_data["regime"])
    
    # Get signals
    engine = SignalEngine()
    signals = await engine.calculate_all_signals(
        db, regime.value, 
        regime_data["oil_change_24h"],
        regime_data["gold_change_24h"]
    )
    
    signal_values = {asset: s.signal_value for asset, s in signals.items()}
    
    # Calculate allocation
    alloc_engine = AllocationEngine()
    current = await alloc_engine.get_current_allocation(db)
    
    new_allocation = await alloc_engine.calculate_and_save(
        db, signal_values, regime, "TIGHT"
    )
    
    # Calculate changes
    changes = {}
    if current:
        changes = {
            "ETH": new_allocation.eth_weight - current.eth_weight,
            "BTC": new_allocation.btc_weight - current.btc_weight,
            "GOLD": new_allocation.gold_weight - current.gold_weight,
            "CASH": new_allocation.cash_weight - current.cash_weight
        }
    
    return {
        "success": True,
        "data": {
            "previous_weights": {
                "ETH": current.eth_weight if current else 0,
                "BTC": current.btc_weight if current else 0,
                "GOLD": current.gold_weight if current else 0,
                "CASH": current.cash_weight if current else 0
            } if current else None,
            "new_weights": {
                "ETH": new_allocation.eth_weight,
                "BTC": new_allocation.btc_weight,
                "GOLD": new_allocation.gold_weight,
                "CASH": new_allocation.cash_weight
            },
            "changes": changes if changes else None,
            "regime": regime.value
        }
    }
