from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.allocation import router as allocation_router
from app.api.prices import router as prices_router
from app.api.regime import router as regime_router
from app.api.signals import router as signals_router
from app.database import init_db
from app.scheduler import shutdown, start

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as exc:
        logger.error("database_init_error", error=str(exc))

    try:
        start()
    except Exception as exc:
        logger.error("scheduler_start_error", error=str(exc))

    yield

    # Shutdown
    try:
        shutdown()
    except Exception as exc:
        logger.error("scheduler_shutdown_error", error=str(exc))


app = FastAPI(
    title="Findicators - Macro Financial Dashboard",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prices_router)
app.include_router(signals_router)
app.include_router(regime_router)
app.include_router(allocation_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
