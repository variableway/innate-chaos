"""Configuration settings for HyperTrace backend."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "HyperTrace"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "sqlite:///./hypertrace.db"
    
    # API Keys
    HYPERLIQUID_API_URL: str = "https://api.hyperliquid.xyz"
    COINGECKO_API_KEY: Optional[str] = None
    
    # Scheduler
    FETCH_INTERVAL_MINUTES: int = 5
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Assets configuration
    ASSETS: dict = {
        "ETH": {"symbol": "ETH", "name": "Ethereum", "hl_symbol": "ETH"},
        "BTC": {"symbol": "BTC", "name": "Bitcoin", "hl_symbol": "BTC"},
        "OIL": {"symbol": "OIL", "name": "Crude Oil", "hl_symbol": "OIL"},
        "GOLD": {"symbol": "GOLD", "name": "Gold", "cg_id": "tether-gold"}
    }
    
    # Signal thresholds
    SIGNAL_THRESHOLDS: dict = {
        "STRONG": 0.7,
        "MODERATE": 0.5,
        "WEAK": 0.3
    }
    
    # Regime thresholds
    REGIME_THRESHOLDS: dict = {
        "RISK_OFF_OIL": 0.05,      # OIL > +5%
        "RISK_OFF_GOLD": 0.00,     # GOLD > 0%
        "RISK_ON_OIL": -0.03,      # OIL < -3%
        "RISK_ON_GOLD": 0.00       # GOLD <= 0%
    }
    
    # Rebalance threshold
    REBALANCE_THRESHOLD: float = 0.1  # 10%
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
