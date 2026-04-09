from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SuggestionData(BaseModel):
    summary: str
    actions: list[str]


class RegimeResponse(BaseModel):
    timestamp: datetime
    regime: str
    risk_score: float
    factor_scores: dict[str, float]
    description: str
    suggestion: SuggestionData


class AllocationResponse(BaseModel):
    timestamp: datetime
    regime: str
    weights: dict[str, float]
