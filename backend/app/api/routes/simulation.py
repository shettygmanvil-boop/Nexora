"""
Simulation Router
=================
Provides endpoints to run and test CrewAI travel planning simulations.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from crewai import Crew
import json
import re

from app.agents.budget_agent.agent import budget_optimization_agent, get_budget_optimization_agent
from app.agents.budget_agent.tasks import get_budget_optimization_task
from app.agents.conflict_agent.conflict_agent import conflict_resolution_agent, get_conflict_resolution_agent
from app.agents.conflict_agent.conflict_tasks import get_conflict_resolution_task
from app.agents.dynamic_sim_agent.agent import dynamic_simulation_agent, get_dynamic_simulation_agent
from app.agents.dynamic_sim_agent.tasks import get_dynamic_simulation_task

from typing import List, Optional

router = APIRouter()

def parse_crew_json(output):
    """
    Helper function to parse CrewAI output string into a dictionary/JSON.
    """
    output_str = str(output)
    try:
        clean_str = output_str.strip()
        if clean_str.startswith("```json"):
            clean_str = clean_str[7:]
        elif clean_str.startswith("```"):
            clean_str = clean_str[3:]
        if clean_str.endswith("```"):
            clean_str = clean_str[:-3]
        clean_str = clean_str.strip()
        return json.loads(clean_str)
    except Exception:
        # Fallback regex search for JSON block
        try:
            match = re.search(r'\{.*\}', output_str, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
        return {"raw_output": output_str}

class SimulationRequest(BaseModel):
    total_budget: float
    traveler_count: int
    demographic_notes: str
    budget_slider_value: dict
    sub_groups: List[str] = []

@router.post("/run-budget-simulation")
async def run_budget_simulation(payload: SimulationRequest):
    """
    Kicks off a budget optimization simulation using CrewAI.
    """
    try:
        agent = get_budget_optimization_agent()
        task = get_budget_optimization_task(
            agent=agent,
            total_budget=payload.total_budget,
            traveler_count=payload.traveler_count,
            demographic_notes=payload.demographic_notes,
            budget_slider_value=payload.budget_slider_value
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task]
        )
        
        result = await crew.kickoff_async()
        return {
            "status": "success",
            "data": parse_crew_json(result)
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }


class ConflictResolutionRequest(BaseModel):
    traveler_profiles: list
    trip_context: str
    sub_groups: List[str] = ["Teenagers who love beaches", "Parents who prefer temples"]

@router.post("/conflict-resolution")
async def run_conflict_resolution(payload: ConflictResolutionRequest):
    """
    Kicks off a conflict resolution simulation using CrewAI.
    Accepts clashing traveler preferences and returns a compromise itinerary.
    """
    try:
        agent = get_conflict_resolution_agent()
        task = get_conflict_resolution_task(
            agent=agent,
            traveler_profiles=payload.traveler_profiles,
            trip_context=payload.trip_context,
            sub_groups=payload.sub_groups,
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
        )

        result = await crew.kickoff_async()
        return {
            "status": "success",
            "data": parse_crew_json(result),
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }


@router.post("/group-solo-split")
async def group_solo_split(payload: ConflictResolutionRequest):
    """
    Kicks off a conflict resolution crew to generate group and solo split itineraries.
    Uses the Conflict Resolution Agent to balance interests, split itineraries, and design reunions.
    """
    try:
        agent = get_conflict_resolution_agent()
        task = get_conflict_resolution_task(
            agent=agent,
            traveler_profiles=payload.traveler_profiles,
            trip_context=payload.trip_context,
            sub_groups=payload.sub_groups,
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
        )

        result = await crew.kickoff_async()
        return {
            "status": "success",
            "data": parse_crew_json(result),
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }


@router.post("/smart-budget-expand")
async def smart_budget_expand(payload: SimulationRequest):
    """
    Kicks off the budget optimization crew focusing on expansion/upgrade options.
    """
    try:
        agent = get_budget_optimization_agent()
        task = get_budget_optimization_task(
            agent=agent,
            total_budget=payload.total_budget,
            traveler_count=payload.traveler_count,
            demographic_notes=payload.demographic_notes,
            budget_slider_value=payload.budget_slider_value
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task]
        )
        
        result = await crew.kickoff_async()
        parsed = parse_crew_json(result)
        
        return {
            "status": "success",
            "data": parsed
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }


class DynamicSimRequest(BaseModel):
    original_plan: dict
    parameter_changes: dict

@router.post("/dynamic-simulate")
async def run_dynamic_simulate(payload: DynamicSimRequest):
    """
    Kicks off a dynamic simulation task when travel parameters change.
    """
    try:
        agent = get_dynamic_simulation_agent()
        task = get_dynamic_simulation_task(
            agent=agent,
            original_plan=payload.original_plan,
            parameter_changes=payload.parameter_changes
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task]
        )
        
        result = await crew.kickoff_async()
        return {
            "status": "success",
            "data": parse_crew_json(result)
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }

