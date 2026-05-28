"""
Conflict Resolution Agent – CrewAI Agent Definition
=====================================================
Instantiates the CrewAI Agent responsible for mediating clashing
traveler preferences and producing win-win group compromises.
"""

from crewai import Agent, LLM

from app.agents.conflict_agent.conflict_prompts import (
    CONFLICT_AGENT_ROLE,
    CONFLICT_AGENT_GOAL,
    CONFLICT_AGENT_BACKSTORY,
)

llm = LLM(
    model="gemini/gemini-3.5-flash",
    api_key="AIzaSyDo1kOidZdeDMPBs6QYpEXuP-38EOv3XZQ",
)

conflict_resolution_agent: Agent = Agent(
    role=CONFLICT_AGENT_ROLE,
    goal=CONFLICT_AGENT_GOAL,
    backstory=CONFLICT_AGENT_BACKSTORY,
    verbose=True,
    allow_delegation=False,
    llm=llm,
)
