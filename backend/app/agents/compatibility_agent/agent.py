from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crewai import Agent
else:
    try:
        from crewai import Agent
    except ImportError:
        Agent = None

from app.agents.compatibility_agent.prompts import EXPECTATION_ANALYSIS_ROLE, EXPECTATION_ANALYSIS_BACKSTORY

def create_expectation_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed.")
    return Agent(
        role=EXPECTATION_ANALYSIS_ROLE,
        goal="Determine how closely a destination matches a user's expectations using real-world characteristics.",
        backstory=EXPECTATION_ANALYSIS_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
