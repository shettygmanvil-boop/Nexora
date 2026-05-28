from crewai import Agent
from app.agents.budget_agent.prompts import BUDGET_SYSTEM_PROMPT
from app.config import shared_llm

def get_budget_optimization_agent() -> Agent:
    return Agent(
        role="AI Budget Optimization Agent",
        goal="Maximize travel value within group budget constraints, handle real-time slider updates, and identify smart expansion opportunities.",
        backstory=BUDGET_SYSTEM_PROMPT,
        verbose=True,
        allow_delegation=False,
        llm=shared_llm,
    )

budget_optimization_agent = get_budget_optimization_agent()
