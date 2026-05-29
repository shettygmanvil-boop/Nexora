from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crewai import Agent
else:
    try:
        from crewai import Agent
    except ImportError:
        Agent = None

from app.agents.accommodation_agent.prompts import ACCOMMODATION_INTEL_ROLE, ACCOMMODATION_INTEL_BACKSTORY

def create_accommodation_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed.")
    return Agent(
        role=ACCOMMODATION_INTEL_ROLE,
        goal="Select optimal lodging options and analyze guest reviews to highlight suitability.",
        backstory=ACCOMMODATION_INTEL_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
