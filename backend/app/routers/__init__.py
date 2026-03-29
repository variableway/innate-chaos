"""API routers."""

from app.routers.prices import router as prices_router
from app.routers.signals import router as signals_router
from app.routers.allocation import router as allocation_router
from app.routers.dashboard import router as dashboard_router

__all__ = ["prices_router", "signals_router", "allocation_router", "dashboard_router"]
