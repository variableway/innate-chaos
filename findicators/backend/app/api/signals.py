from datetime import datetime

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.signal import SignalData, SignalResponse
from app.services.signal_engine import SignalEngine

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/signals", tags=["signals"])


@router.get("/current", response_model=SignalResponse)
async def get_current_signals(db: AsyncSession = Depends(get_db)):
    """Return current risk signals and factor breakdown."""
    engine = SignalEngine(db)
    result = await engine.calculate_risk_score()

    signals: dict[str, SignalData] = {}
    factor_scores = result.get("factor_scores", {})

    for factor, score in factor_scores.items():
        signals[factor] = SignalData(
            value=score,
            action=_classify_action(score),
            breakdown=None,
        )

    # Add composite signal
    signals["composite"] = SignalData(
        value=result["risk_score"],
        action=result["regime"],
        breakdown=factor_scores,
    )

    return SignalResponse(
        timestamp=datetime.utcnow(),
        signals=signals,
    )


def _classify_action(score: float) -> str:
    if score >= 0.6:
        return "RISK_ON"
    elif score <= 0.4:
        return "RISK_OFF"
    return "NEUTRAL"
