from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.regime import AllocationResponse, RegimeResponse, SuggestionData
from app.services.allocation_engine import AllocationEngine
from app.services.risk_engine import RiskEngine

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/regime", tags=["regime"])


@router.get("/current", response_model=RegimeResponse)
async def get_current_regime(db: AsyncSession = Depends(get_db)):
    """Return the current regime assessment."""
    engine = RiskEngine(db)
    record = await engine.get_current_regime()

    if record is None:
        # No record yet -- compute on the fly
        result = await engine.assess()
        return RegimeResponse(
            timestamp=datetime.utcnow(),
            regime=result["regime"],
            risk_score=result["risk_score"],
            factor_scores=result.get("factor_scores", {}),
            description=result.get("description", ""),
            suggestion=SuggestionData(**result.get("suggestion", {"summary": "", "actions": []})),
        )

    suggestion = SuggestionData(
        summary=_suggestion_for_regime(record.regime)["summary"],
        actions=_suggestion_for_regime(record.regime)["actions"],
    )

    return RegimeResponse(
        timestamp=record.time,
        regime=record.regime,
        risk_score=float(record.risk_score),
        factor_scores=record.factor_scores or {},
        description=record.description or "",
        suggestion=suggestion,
    )


@router.get("/history")
async def get_regime_history(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Return regime history for the last N days."""
    engine = RiskEngine(db)
    history = await engine.get_regime_history(days)

    return [
        {
            "timestamp": h.time,
            "regime": h.regime,
            "risk_score": float(h.risk_score),
            "factor_scores": h.factor_scores or {},
            "description": h.description or "",
        }
        for h in history
    ]


def _suggestion_for_regime(regime: str) -> dict:
    if regime == "RISK_ON":
        return {
            "summary": "Risk appetite is elevated. Consider increasing exposure to growth assets.",
            "actions": [
                "Increase crypto allocation",
                "Reduce cash and defensive positions",
                "Monitor BTC momentum for reversal signals",
            ],
        }
    elif regime == "RISK_OFF":
        return {
            "summary": "Risk aversion is high. Consider shifting to defensive positions.",
            "actions": [
                "Increase gold and cash allocation",
                "Reduce crypto exposure",
                "Watch yield curve for further inversion",
            ],
        }
    return {
        "summary": "Markets are in a neutral state. Maintain balanced allocation.",
        "actions": [
            "Hold current allocation",
            "Diversify across asset classes",
            "Stay alert for regime changes",
        ],
    }
