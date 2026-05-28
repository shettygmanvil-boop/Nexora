"""
Crew Setup and Orchestration
=============================
Initializes and coordinates the CrewAI agents and tasks for Maproom.
"""

from crewai import Crew
from app.agents.budget_agent.agent import budget_optimization_agent
from app.agents.budget_agent.tasks import get_budget_optimization_task
from app.agents.conflict_agent.conflict_agent import conflict_resolution_agent
from app.agents.conflict_agent.conflict_tasks import get_conflict_resolution_task
from app.agents.dynamic_sim_agent.agent import dynamic_simulation_agent
from app.agents.dynamic_sim_agent.tasks import get_dynamic_simulation_task

class MapRoomOrchestrator:
    """
    Orchestrates the agents and tasks to produce optimized itineraries and simulations.
    """
    
    @staticmethod
    def get_budget_crew(total_budget: float, traveler_count: int, demographic_notes: str, budget_slider_value: dict) -> Crew:
        task = get_budget_optimization_task(
            agent=budget_optimization_agent,
            total_budget=total_budget,
            traveler_count=traveler_count,
            demographic_notes=demographic_notes,
            budget_slider_value=budget_slider_value
        )
        return Crew(
            agents=[budget_optimization_agent],
            tasks=[task],
            verbose=True
        )
        
    @staticmethod
    def get_conflict_crew(traveler_profiles: list, trip_context: str, sub_groups: list = None) -> Crew:
        if sub_groups is None:
            sub_groups = ["Teenagers who love nightlife", "Parents who prefer peaceful nature"]
        task = get_conflict_resolution_task(
            agent=conflict_resolution_agent,
            traveler_profiles=traveler_profiles,
            trip_context=trip_context,
            sub_groups=sub_groups
        )
        return Crew(
            agents=[conflict_resolution_agent],
            tasks=[task],
            verbose=True
        )

    @staticmethod
    def get_simulation_crew(original_plan: dict, parameter_changes: dict) -> Crew:
        task = get_dynamic_simulation_task(
            agent=dynamic_simulation_agent,
            original_plan=original_plan,
            parameter_changes=parameter_changes
        )
        return Crew(
            agents=[dynamic_simulation_agent],
            tasks=[task],
            verbose=True
        )
