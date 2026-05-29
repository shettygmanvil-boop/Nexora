"""
Dynamic Simulation Agent – CrewAI Agent Definition
=====================================================
Instantiates the CrewAI Agent responsible for executing real-time travel planning simulations.
"""

try:
    from crewai import Agent
except ImportError:
    Agent = None
from app.agents.llm_utils import get_llm
from app.agents.dynamic_sim_agent.prompts import (
    DYNAMIC_SIM_ROLE,
    DYNAMIC_SIM_GOAL,
    DYNAMIC_SIM_BACKSTORY,
)

def get_dynamic_simulation_agent() -> Agent:
    if Agent is None:
        raise RuntimeError("crewai is not installed")
    return Agent(
        role=DYNAMIC_SIM_ROLE,
        goal=DYNAMIC_SIM_GOAL,
        backstory=DYNAMIC_SIM_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        llm=get_llm(),
    )


