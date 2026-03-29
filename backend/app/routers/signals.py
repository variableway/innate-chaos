"""Signals API router."""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from models.signal import Signal
from services.risk_classifier import RiskClassifier

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/current")
async def get_current_signals(db: AsyncSession = Depends(get_db)):
    """Get current signals for all assets."""
    assets = ["ETH", "BTC", "GOLD"]
    signals = []
    
    for asset in assets:
        query = select(Signal).where(
            Signal.asset == asset
        ).order_by(desc(Signal.time)).limit(1)
        
        result = await db.execute(query)
        signal = result.scalar_one_or_none()
        
        if signal:
            signal_dict = signal.to_dict()
            signal_dict["action"] = signal.get_action()
            signal_dict["action_text"] = signal.get_action_text()
            signals.append(signal_dict)
    
    # Get current regime
    classifier = RiskClassifier()
    regime_data = await classifier.get_current_regime(db)
    
    return {
        "success": True,
        "data": {
            "time": datetime.utcnow().isoformat(),
            "regime": regime_data["regime"],
            "signals": signals
        }
    }


@router.get("/{asset}")
async def get_signal_history(
    asset: str,
    limit: int = Query(168, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get signal history for an asset."""
    asset = asset.upper()
    
    query = select(Signal).where(
        Signal.asset == asset
    ).order_by(desc(Signal.time)).limit(limit)
    
    result = await db.execute(query)
    signals = result.scalars().all()
    
    return {
        "success": True,
        "data": {
            "asset": asset,
            "count": len(signals),
            "signals": [s.to_dict() for s in signals]
        }
    }


@router.get("/{asset}/latest")
async def get_latest_signal(asset: str, db: AsyncSession = Depends(get_db)):
    """Get latest signal for an asset."""
    asset = asset.upper()
    
    query = select(Signal).where(
        Signal.asset == asset
    ).order_by(desc(Signal.time)).limit(1)
    
    result = await db.execute(query)
    signal = result.scalar_one_or_none()
    
    if not signal:
        raise HTTPException(status_code=404, detail=f"No signal data for {asset}")
    
    signal_dict = signal.to_dict()
    signal_dict["action"] = signal.get_action()
    signal_dict["action_text"] = signal.get_action_text()
    
    return {
        "success": True,
        "data": signal_dict
    }
