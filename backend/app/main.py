"""
Maproom Backend Orchestrator
============================
Main FastAPI application entry point. Registers routers, middleware,
and provides basic server health checks.
"""

from fastapi import FastAPI
from app.api.routes.simulation import router as simulation_router

# 1. Initialize FastAPI application instance
app = FastAPI(
    title="Maproom Backend Orchestrator",
    description="CrewAI-powered travel orchestration platform backend API",
    version="1.0.0"
)

# 2. Register routers
app.include_router(
    simulation_router,
    prefix="/api/v1/simulation",
    tags=["Simulation"]
)

# 3. Root health check endpoint
@app.get("/")
async def root():
    """
    Service health check endpoint.
    """
    return {"message": "Maproom Backend Orchestrator is Running"}
