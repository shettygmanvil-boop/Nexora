"""
Conflict Resolution Agent – CrewAI Agent Definition
=====================================================
Instantiates the CrewAI Agent responsible for mediating clashing
traveler preferences and producing win-win group compromises.
"""

from crewai import Agent
from app.config import shared_llm
from app.agents.conflict_agent.conflict_prompts import (
    CONFLICT_AGENT_ROLE,
    CONFLICT_AGENT_GOAL,
    CONFLICT_AGENT_BACKSTORY,
)

def get_conflict_resolution_agent() -> Agent:
    return Agent(
        role=CONFLICT_AGENT_ROLE,
        goal=CONFLICT_AGENT_GOAL,
        backstory=CONFLICT_AGENT_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        llm=shared_llm,
    )

conflict_resolution_agent = get_conflict_resolution_agent()
