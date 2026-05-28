"""
Conflict Resolution Agent – CrewAI Agent Definition
=====================================================
Instantiates the CrewAI Agent responsible for mediating clashing
traveler preferences and producing win-win group compromises.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly find and load the .env file from the project root
# (Using parents[4] to go from backend/app/agents/conflict_agent/conflict_agent.py -> project root)
env_path = Path(__file__).resolve().parents[4] / '.env'
load_dotenv(dotenv_path=env_path)

from crewai import Agent, LLM

from app.agents.conflict_agent.conflict_prompts import (
    CONFLICT_AGENT_ROLE,
    CONFLICT_AGENT_GOAL,
    CONFLICT_AGENT_BACKSTORY,
)

llm = LLM(
    model="gemini/gemini-3.5-flash",
    api_key=os.environ.get("GEMINI_API_KEY"),
)

conflict_resolution_agent: Agent = Agent(
    role=CONFLICT_AGENT_ROLE,
    goal=CONFLICT_AGENT_GOAL,
    backstory=CONFLICT_AGENT_BACKSTORY,
    verbose=True,
    allow_delegation=False,
    llm=llm,
)
