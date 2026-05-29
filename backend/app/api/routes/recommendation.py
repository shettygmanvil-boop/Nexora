from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.travel import (
    TravelGroupRequest, 
    RecommendationResponse, 
    SimulationResponse,
    TravelerProfile
)
from app.schemas.trip import GroupTripRequest, RecommendationDetails
from app.services.crew_service import run_travel_recommendation_crew
from app.services.simulation import simulate_budget_adjustment
from app.database.mock_db import list_destinations
from app.services.recommendation_service import get_recommendations as get_recommendations_service

router = APIRouter(prefix="/recommendation", tags=["Recommendation Engine"])

@router.post("/", response_model=RecommendationResponse)
def get_recommendations(request: TravelGroupRequest):
    """
    Triggers the multi-agent travel orchestration planner.
    Analyzes traveler compatibility, medical parameters, budgets, and creates group/solo itineraries.
    """
    try:
        recommendation = run_travel_recommendation_crew(request)
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")

@router.get("/destinations", response_model=List[str])
def get_available_destinations():
    """
    List all travel destinations supported in the prototype.
    """
    return list_destinations()

@router.post("/simulate", response_model=SimulationResponse)
def simulate_trip(
    destination: str,
    target_budget: float,
    num_days: int,
    travelers: List[TravelerProfile]
):
    """
    Simulates modifications to accommodation matching, itineraries, and upgrades in real-time
    when adjusting the travel budget slider.
    """
    try:
        return simulate_budget_adjustment(
            destination_name=destination,
            target_budget=target_budget,
            num_days=num_days,
            travelers=travelers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


# Router for root-level /recommend route to avoid /recommendation prefix collision
recommend_router = APIRouter(prefix="", tags=["Recommendation Engine"])

@recommend_router.post("/recommend", response_model=List[RecommendationDetails])
def recommend_destinations(request: GroupTripRequest):
    """
    Intelligent recommendation engine route.
    Calculates detailed suitability scores, matches expectations,
    generates warnings, and returns a ranked list of destinations.
    """
    try:
        return get_recommendations_service(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation engine failure: {str(e)}")

