"""
Maproom Backend Orchestrator
============================
Main FastAPI application entry point. Registers routers, middleware,
and diagnostic health checks for all merged features (simulation,
weather intelligence, travel recommendations, and trip validation).
"""

from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Route Imports
from app.api.routes.simulation import router as simulation_router
from app.api.routes.weather import router as weather_router
from app.api.routes.recommendation import router as recommendation_router
from app.api.routes.recommendation import recommend_router
from app.api.routes.trip import router as trip_router

from app.models.trip import GroupTripRequest
from app.services.recommendation_service import get_recommendations

# 1. Initialize FastAPI application instance
app = FastAPI(
    title="Maproom Backend Orchestrator",
    description="CrewAI-powered travel orchestration platform backend API (Integrated)",
    version="1.0.0"
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev/hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Register routers
# Simulation routes (Manvil branch)
app.include_router(
    simulation_router,
    prefix="/api/v1/simulation",
    tags=["Simulation"]
)

# Weather intelligence routes (smaran branch)
app.include_router(
    weather_router,
    prefix="/api",
    tags=["Weather Intelligence"]
)

# Recommendation routes (pratyush branch)
app.include_router(recommendation_router)
app.include_router(recommend_router)

# Trip and destinations routes (pratyush branch)
app.include_router(trip_router)


# 3. Diagnostics and Root Routes
@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint welcome message.
    """
    return {
        "message": "Welcome to Maproom - The AI-Powered Travel Recommendation System",
        "documentation": "/docs",
        "health_check": "/health",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """
    Unified diagnostic health check.
    """
    return {
        "status": "healthy",
        "app": "Maproom Backend Orchestrator",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }


# Crew Recommendation Route
@app.post("/crew-recommend", tags=["Recommendation Engine"])
async def crew_recommend(request: GroupTripRequest):
    """
    Direct route to get deterministic recommendations as a fallback/compatibility route.
    """
    return {
        "mode": "crew_fallback",
        "message": "CrewAI route connected successfully.",
        "recommendations": get_recommendations(request),
    }
