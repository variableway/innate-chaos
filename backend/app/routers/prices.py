"""Prices API router."""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from models.price import Price

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/current")
async def get_current_prices(db: AsyncSession = Depends(get_db)):
    """Get current prices for all assets."""
    assets = ["ETH", "BTC", "GOLD", "OIL"]
    prices = []
    
    for asset in assets:
        query = select(Price).where(
            Price.asset == asset
        ).order_by(desc(Price.time)).limit(1)
        
        result = await db.execute(query)
        price = result.scalar_one_or_none()
        
        if price:
            prices.append(price.to_dict())
    
    return {
        "success": True,
        "data": {
            "time": datetime.utcnow().isoformat(),
            "prices": prices
        }
    }


@router.get("/{asset}")
async def get_price_history(
    asset: str,
    limit: int = Query(100, ge=1, le=1000),
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get price history for an asset."""
    asset = asset.upper()
    
    query = select(Price).where(Price.asset == asset)
    
    if from_date:
        query = query.where(Price.time >= from_date)
    if to_date:
        query = query.where(Price.time <= to_date)
    else:
        # Default to last 7 days
        query = query.where(Price.time >= datetime.utcnow() - timedelta(days=7))
    
    query = query.order_by(desc(Price.time)).limit(limit)
    
    result = await db.execute(query)
    prices = result.scalars().all()
    
    return {
        "success": True,
        "data": {
            "asset": asset,
            "count": len(prices),
            "prices": [p.to_dict() for p in prices]
        }
    }


@router.get("/{asset}/latest")
async def get_latest_price(asset: str, db: AsyncSession = Depends(get_db)):
    """Get latest price for an asset."""
    asset = asset.upper()
    
    query = select(Price).where(
        Price.asset == asset
    ).order_by(desc(Price.time)).limit(1)
    
    result = await db.execute(query)
    price = result.scalar_one_or_none()
    
    if not price:
        raise HTTPException(status_code=404, detail=f"No price data for {asset}")
    
    return {
        "success": True,
        "data": price.to_dict()
    }
