import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import health, recommendation, trip
from backend.utils.config import settings

# Initialize the FastAPI Application
app = FastAPI(
    title="Maproom AI Travel Backend",
    description="Multi-agent travel recommendation and group conflict resolution orchestration backend.",
    version="1.0.0",
)

# Set up CORS middleware to allow connection from potential web frontends or external API requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health.router)
app.include_router(recommendation.router)
app.include_router(recommendation.recommend_router)
app.include_router(trip.router)

# Default root route redirecting to standard information
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Maproom - The AI-Powered Travel Recommendation System",
        "documentation": "/docs",
        "health_check": "/health"
    }

if __name__ == "__main__":
    # Start the server locally using configuration variables
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
