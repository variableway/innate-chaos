from datetime import datetime

from pydantic import BaseModel


class SignalData(BaseModel):
    value: float
    action: str
    breakdown: dict[str, float] | None = None


class SignalResponse(BaseModel):
    timestamp: datetime
    signals: dict[str, SignalData]
