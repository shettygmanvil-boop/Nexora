from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crewai import Agent
else:
    try:
        from crewai import Agent
    except ImportError:
        Agent = None

from app.agents.preference_agent.prompts import PREFERENCE_ANALYSIS_ROLE, PREFERENCE_ANALYSIS_BACKSTORY

def create_preference_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed.")
    return Agent(
        role=PREFERENCE_ANALYSIS_ROLE,
        goal="Analyze traveler demographics, vibes, and preferences to find common ground and conflicts.",
        backstory=PREFERENCE_ANALYSIS_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
