"""
Conflict Resolution Agent – CrewAI Agent Definition
=====================================================
Instantiates the CrewAI Agent responsible for mediating clashing
traveler preferences and producing win-win group compromises.
"""

try:
    from crewai import Agent
except ImportError:
    Agent = None
from app.agents.llm_utils import get_llm
from app.agents.conflict_agent.conflict_prompts import (
    CONFLICT_AGENT_ROLE,
    CONFLICT_AGENT_GOAL,
    CONFLICT_AGENT_BACKSTORY,
)

def get_conflict_resolution_agent() -> Agent:
    if Agent is None:
        raise RuntimeError("crewai is not installed")
    return Agent(
        role=CONFLICT_AGENT_ROLE,
        goal=CONFLICT_AGENT_GOAL,
        backstory=CONFLICT_AGENT_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        llm=get_llm(),
    )


