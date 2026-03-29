"""HyperTrace Backend - FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_db
from app.routers import prices_router, signals_router, allocation_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting up HyperTrace backend...")
    await init_db()
    
    # Start scheduler
    from app.scheduler import start_scheduler, stop_scheduler
    start_scheduler()
    
    yield
    
    # Shutdown
    logger.info("Shutting down HyperTrace backend...")
    stop_scheduler()
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Trading signal and allocation API using HyperLiquid data",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prices_router, prefix="/api/v1")
app.include_router(signals_router, prefix="/api/v1")
app.include_router(allocation_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/dashboard")
async def get_dashboard():
    """Get full dashboard data."""
    from fastapi import Depends
    from app.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession
    from services.risk_classifier import RiskClassifier
    from services.data_fetcher import DataFetcher
    
    # This is a placeholder - in real implementation, 
    # you'd aggregate data from multiple sources
    return {
        "success": True,
        "data": {
            "message": "Dashboard data endpoint - implement aggregation logic"
        }
    }


# Import datetime at the end to avoid circular issues
from datetime import datetime

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
