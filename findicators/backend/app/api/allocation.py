from datetime import datetime

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.regime import AllocationResponse
from app.services.allocation_engine import AllocationEngine
from app.services.risk_engine import RiskEngine

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/allocation", tags=["allocation"])


@router.get("/current", response_model=AllocationResponse)
async def get_current_allocation(db: AsyncSession = Depends(get_db)):
    """Return suggested allocation based on current regime."""
    risk_engine = RiskEngine(db)
    record = await risk_engine.get_current_regime()

    regime = record.regime if record else "NEUTRAL"
    allocation = AllocationEngine.get_allocation(regime)

    return AllocationResponse(
        timestamp=datetime.utcnow(),
        regime=allocation["regime"],
        weights=allocation["weights"],
    )
