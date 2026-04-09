from datetime import datetime, timedelta, timezone

import numpy as np
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.price import Price

logger = structlog.get_logger()

# Factor weights
FACTOR_WEIGHTS = {
    "oil_trend": 0.20,
    "gold_trend": 0.25,
    "btc_momentum": 0.25,
    "yield_curve": 0.20,
    "volatility": 0.10,
}


class SignalEngine:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = settings

    async def calculate_trend(self, asset: str, days: int) -> float:
        """Calculate N-day percentage change for an asset. Returns 0.0 if insufficient data."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(Price.price)
            .where(Price.asset == asset, Price.time >= cutoff)
            .order_by(Price.time.asc())
        )
        result = await self.db.execute(stmt)
        prices = [float(row[0]) for row in result.all()]

        if len(prices) < 2:
            logger.warning("insufficient_data_for_trend", asset=asset, days=days, data_points=len(prices))
            return 0.0

        old_price = prices[0]
        new_price = prices[-1]

        if old_price == 0:
            return 0.0

        return (new_price - old_price) / old_price

    @staticmethod
    def normalize(value: float, threshold: float) -> float:
        """Map a value to a 0-1 range using the threshold as the denominator."""
        if threshold == 0:
            return 0.5
        clamped = max(-threshold, min(threshold, value))
        return (clamped / threshold + 1.0) / 2.0

    async def calculate_volatility(self, assets: list[str], days: int) -> float:
        """Calculate portfolio-like volatility across given assets. Returns 0.0-1.0 score."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        all_returns: list[float] = []
        for asset in assets:
            stmt = (
                select(Price.price)
                .where(Price.asset == asset, Price.time >= cutoff)
                .order_by(Price.time.asc())
            )
            result = await self.db.execute(stmt)
            prices = [float(row[0]) for row in result.all()]

            if len(prices) < 2:
                continue

            returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices)) if prices[i - 1] != 0]
            all_returns.extend(returns)

        if not all_returns:
            return 0.5

        vol = float(np.std(all_returns))
        # Normalize: annualized vol of crypto ~0.80 as "high", 0 as "low"
        # Scale daily vol: rough mapping
        return min(1.0, vol * 100.0)

    async def calculate_risk_score(self) -> dict:
        """Calculate the composite risk score and return full assessment."""
        try:
            # Oil trend (7-day)
            oil_trend = await self.calculate_trend("OIL", self.settings.oil_trend_days)
            oil_score = self.normalize(oil_trend, 0.05)  # 5% threshold

            # Gold trend (7-day) -- rising gold is risk-off signal, so invert
            gold_trend = await self.calculate_trend("GOLD", self.settings.gold_trend_days)
            gold_score = 1.0 - self.normalize(gold_trend, 0.05)

            # BTC momentum (7-day)
            btc_trend = await self.calculate_trend("BTC", self.settings.btc_momentum_days)
            btc_score = self.normalize(btc_trend, 0.10)

            # Yield curve (T10Y2Y) -- inverted (negative) is risk-off
            yield_curve_trend = await self.calculate_trend("T10Y2Y", 7)
            yield_score = self.normalize(yield_curve_trend, 0.02)

            # Volatility across crypto
            vol_score = await self.calculate_volatility(["BTC", "ETH"], self.settings.volatility_window)

            factor_scores = {
                "oil_trend": round(oil_score, 4),
                "gold_trend": round(gold_score, 4),
                "btc_momentum": round(btc_score, 4),
                "yield_curve": round(yield_score, 4),
                "volatility": round(vol_score, 4),
            }

            # Composite risk score
            risk_score = sum(
                FACTOR_WEIGHTS[k] * factor_scores[k] for k in FACTOR_WEIGHTS
            )
            risk_score = round(risk_score, 4)

            # Regime classification
            if risk_score >= self.settings.risk_on_threshold:
                regime = "RISK_ON"
            elif risk_score <= self.settings.risk_off_threshold:
                regime = "RISK_OFF"
            else:
                regime = "NEUTRAL"

            # Description
            description = self._build_description(regime, risk_score, factor_scores)

            # Suggestion
            suggestion = self._build_suggestion(regime, risk_score, factor_scores)

            return {
                "risk_score": risk_score,
                "regime": regime,
                "factor_scores": factor_scores,
                "description": description,
                "suggestion": suggestion,
            }

        except Exception as exc:
            logger.error("risk_score_calculation_error", error=str(exc))
            return {
                "risk_score": 0.5,
                "regime": "NEUTRAL",
                "factor_scores": {},
                "description": f"Error calculating risk score: {exc}",
                "suggestion": {"summary": "Unable to assess risk", "actions": []},
            }

    @staticmethod
    def _build_description(regime: str, risk_score: float, factor_scores: dict) -> str:
        parts = [f"Regime: {regime} (score: {risk_score:.2f})."]
        for factor, score in factor_scores.items():
            parts.append(f"{factor}: {score:.2f}")
        return " ".join(parts)

    @staticmethod
    def _build_suggestion(regime: str, risk_score: float, factor_scores: dict) -> dict:
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
        else:
            return {
                "summary": "Markets are in a neutral state. Maintain balanced allocation.",
                "actions": [
                    "Hold current allocation",
                    "Diversify across asset classes",
                    "Stay alert for regime changes",
                ],
            }
