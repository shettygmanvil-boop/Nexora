"""
Dynamic Simulation Agent – CrewAI Agent Definition
=====================================================
Instantiates the CrewAI Agent responsible for executing real-time travel planning simulations.
"""

from crewai import Agent
from app.config import shared_llm
from app.agents.dynamic_sim_agent.prompts import (
    DYNAMIC_SIM_ROLE,
    DYNAMIC_SIM_GOAL,
    DYNAMIC_SIM_BACKSTORY,
)

def get_dynamic_simulation_agent() -> Agent:
    return Agent(
        role=DYNAMIC_SIM_ROLE,
        goal=DYNAMIC_SIM_GOAL,
        backstory=DYNAMIC_SIM_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        llm=shared_llm,
    )

dynamic_simulation_agent = get_dynamic_simulation_agent()
