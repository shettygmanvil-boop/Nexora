"""
Maproom — FastAPI Application Entry Point
==========================================
Bootstraps the application, registers middleware, and mounts all routers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings

# ── Route Imports ─────────────────────────────────────────────────────────────
# Import each router as it is implemented by individual team members.
# Only the weather router is live in Phase 1.
from app.api.routes.weather import router as weather_router

# Future routers (uncomment as each Phase is implemented):
from app.api.routes.trip import router as trip_router
from app.api.routes.itinerary import router as itinerary_router
from app.api.routes.hotels import router as hotels_router
from app.api.routes.simulation import router as simulation_router
from app.api.routes.recommendation import router as recommendation_router
from app.api.routes.recommendation import recommend_router as recommend_router_root
# from app.api.routes.compatibility import router as compatibility_router
# from app.api.routes.auth import router as auth_router

logger = logging.getLogger(__name__)

# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Startup/shutdown logic lives here (DB pool, cache connections, etc.).
    """
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    logger.info("🗺️  Maproom backend starting up — env=%s", settings.app_env)
    yield
    logger.info("🗺️  Maproom backend shutting down")


# ── App Factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Maproom — AI-powered multi-agent intelligent travel planning platform. "
            "Phase 1: Weather Intelligence System."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(weather_router, prefix="/api", tags=["Weather Intelligence"])

    # Future routers (add here as phases are completed):
    app.include_router(trip_router, prefix="/api", tags=["Trip Planning"])
    app.include_router(itinerary_router, prefix="/api", tags=["Itinerary"])
    app.include_router(hotels_router, prefix="/api", tags=["Hotels"])
    app.include_router(simulation_router, prefix="/api", tags=["Simulation"])
    app.include_router(recommendation_router, prefix="/api", tags=["Recommendation Engine"])
    app.include_router(recommend_router_root, prefix="/api", tags=["Recommendation Engine"])

    # ── Health Check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["System"])
    async def health_check():
        return JSONResponse(
            content={
                "status": "healthy",
                "app": settings.app_name,
                "version": settings.app_version,
                "environment": settings.app_env,
            }
        )

    return app


app = create_app()
