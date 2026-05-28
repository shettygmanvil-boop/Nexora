"""
Simulation Router
=================
Provides endpoints to run and test CrewAI travel planning simulations.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from crewai import Crew

from app.agents.budget_agent.agent import budget_optimization_agent
from app.agents.budget_agent.tasks import get_budget_optimization_task
from app.agents.conflict_agent.conflict_agent import conflict_resolution_agent
from app.agents.conflict_agent.conflict_tasks import get_conflict_resolution_task

router = APIRouter()

class SimulationRequest(BaseModel):
    total_budget: float
    traveler_count: int
    demographic_notes: str
    budget_slider_value: dict

@router.post("/run-budget-simulation")
async def run_budget_simulation(payload: SimulationRequest):
    """
    Kicks off a budget optimization simulation using CrewAI.
    """
    # 1. Generate the budget task using request inputs
    task = get_budget_optimization_task(
        agent=budget_optimization_agent,
        total_budget=payload.total_budget,
        traveler_count=payload.traveler_count,
        demographic_notes=payload.demographic_notes,
        budget_slider_value=payload.budget_slider_value
    )
    
    # 2. Assemble the Crew
    crew = Crew(
        agents=[budget_optimization_agent],
        tasks=[task]
    )
    
    # 3. Kick off execution
    result = crew.kickoff()
    
    # 4. Return the outcome
    return {
        "status": "success",
        "data": result
    }


class ConflictResolutionRequest(BaseModel):
    traveler_profiles: list
    trip_context: str


@router.post("/conflict-resolution")
async def run_conflict_resolution(payload: ConflictResolutionRequest):
    """
    Kicks off a conflict resolution simulation using CrewAI.
    Accepts clashing traveler preferences and returns a compromise itinerary.
    """
    # 1. Generate the conflict resolution task
    task = get_conflict_resolution_task(
        agent=conflict_resolution_agent,
        traveler_profiles=payload.traveler_profiles,
        trip_context=payload.trip_context,
    )

    # 2. Assemble the Crew
    crew = Crew(
        agents=[conflict_resolution_agent],
        tasks=[task],
    )

    # 3. Kick off execution (async)
    result = await crew.kickoff_async()

    # 4. Return the compromise itinerary
    return {
        "status": "success",
        "data": result,
    }
