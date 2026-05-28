import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import health, recommendation, trip
from backend.utils.config import settings
from backend.models.trip import GroupTripRequest
from backend.services.recommendation_service import get_recommendations

# Initialize FastAPI App
app = FastAPI(
    title="Maproom AI Travel Backend",
    description="Multi-agent travel recommendation and group conflict resolution orchestration backend.",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health.router)
app.include_router(recommendation.router)
app.include_router(recommendation.recommend_router)
app.include_router(trip.router)


# Root Route
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Maproom - The AI-Powered Travel Recommendation System",
        "documentation": "/docs",
        "health_check": "/health",
    }


# Crew Recommendation Route
@app.post("/crew-recommend")
async def crew_recommend(request: GroupTripRequest):
    return {
        "mode": "crew_fallback",
        "message": "CrewAI route connected successfully.",
        "recommendations": get_recommendations(request),
    }


# Run Server
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )