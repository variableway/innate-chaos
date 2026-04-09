import structlog

logger = structlog.get_logger()

ALLOCATION_TABLE = {
    "RISK_ON": {
        "BTC": 0.30,
        "ETH": 0.20,
        "GOLD": 0.15,
        "OIL": 0.10,
        "CASH": 0.25,
    },
    "NEUTRAL": {
        "BTC": 0.20,
        "ETH": 0.15,
        "GOLD": 0.25,
        "OIL": 0.10,
        "CASH": 0.30,
    },
    "RISK_OFF": {
        "BTC": 0.05,
        "ETH": 0.05,
        "GOLD": 0.40,
        "OIL": 0.05,
        "CASH": 0.45,
    },
}


class AllocationEngine:
    @staticmethod
    def get_allocation(regime: str) -> dict:
        """Return suggested allocation weights for the given regime.

        Falls back to NEUTRAL allocation if regime is unknown.
        """
        weights = ALLOCATION_TABLE.get(regime, ALLOCATION_TABLE["NEUTRAL"])
        return {
            "regime": regime,
            "weights": dict(weights),
        }
