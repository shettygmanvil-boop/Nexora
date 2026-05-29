from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crewai import Agent
else:
    try:
        from crewai import Agent
    except ImportError:
        Agent = None

from app.agents.itinerary_agent.prompts import ITINERARY_PLANNER_ROLE, ITINERARY_PLANNER_BACKSTORY

def create_itinerary_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed.")
    return Agent(
        role=ITINERARY_PLANNER_ROLE,
        goal="Create daily schedules that optimize route flow, travel times, and minimize physical fatigue.",
        backstory=ITINERARY_PLANNER_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
