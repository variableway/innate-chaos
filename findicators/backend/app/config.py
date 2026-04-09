from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # HyperLiquid
    hyperliquid_api_url: str = "https://api.hyperliquid.xyz"

    # FRED
    fred_api_key: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/findicators"

    # Scheduler
    crypto_fetch_interval_seconds: int = 300
    economic_fetch_interval_seconds: int = 86400

    # Signal Engine
    oil_trend_days: int = 7
    gold_trend_days: int = 7
    btc_momentum_days: int = 7
    volatility_window: int = 20
    risk_on_threshold: float = 0.6
    risk_off_threshold: float = 0.4

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
