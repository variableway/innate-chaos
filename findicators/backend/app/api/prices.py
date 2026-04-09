from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.price import PriceData, PriceHistoryPoint, PriceHistoryResponse, PriceResponse
from app.services.price_service import PriceService

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/prices", tags=["prices"])


@router.get("/current", response_model=PriceResponse)
async def get_current_prices(db: AsyncSession = Depends(get_db)):
    """Return current prices for all tracked assets."""
    service = PriceService(db, adapters=[])
    prices = await service.get_current_prices()

    assets: dict[str, PriceData] = {}
    for p in prices:
        assets[p.asset] = PriceData(
            asset=p.asset,
            price=float(p.price),
            source=p.source,
            change_24h=float(p.change_24h) if p.change_24h is not None else None,
            volume_24h=float(p.volume_24h) if p.volume_24h is not None else None,
        )

    return PriceResponse(
        timestamp=datetime.utcnow(),
        assets=assets,
    )


@router.get("/{asset}/history", response_model=PriceHistoryResponse)
async def get_price_history(
    asset: str,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Return price history for a specific asset."""
    service = PriceService(db, adapters=[])
    history = await service.get_price_history(asset, days)

    data = [
        PriceHistoryPoint(
            time=h.time,
            price=float(h.price),
            volume=float(h.volume_24h) if h.volume_24h is not None else None,
        )
        for h in history
    ]

    return PriceHistoryResponse(asset=asset, data=data)
