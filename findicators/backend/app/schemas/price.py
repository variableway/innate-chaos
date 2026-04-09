from datetime import datetime

from pydantic import BaseModel


class PriceData(BaseModel):
    asset: str
    price: float
    source: str
    change_24h: float | None = None
    volume_24h: float | None = None


class PriceResponse(BaseModel):
    timestamp: datetime
    assets: dict[str, PriceData]


class PriceHistoryPoint(BaseModel):
    time: datetime
    price: float
    volume: float | None = None


class PriceHistoryResponse(BaseModel):
    asset: str
    data: list[PriceHistoryPoint]
