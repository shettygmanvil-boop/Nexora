"""
Maproom Backend Orchestrator
============================
Main FastAPI application entry point. Registers routers, middleware,
and provides basic server health checks.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.simulation import router as simulation_router

# 1. Initialize FastAPI application instance
app = FastAPI(
    title="Maproom Backend Orchestrator",
    description="CrewAI-powered travel orchestration platform backend API",
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

