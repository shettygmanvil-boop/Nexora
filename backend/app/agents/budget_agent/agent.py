try:
    from crewai import Agent
except ImportError:
    Agent = None
from app.agents.budget_agent.prompts import BUDGET_SYSTEM_PROMPT
from app.agents.llm_utils import get_llm

def get_budget_optimization_agent() -> Agent:
    if Agent is None:
        raise RuntimeError("crewai is not installed")
    return Agent(
        role="AI Budget Optimization Agent",
        goal="Maximize travel value within group budget constraints, handle real-time slider updates, and identify smart expansion opportunities.",
        backstory=BUDGET_SYSTEM_PROMPT,
        verbose=True,
        allow_delegation=False,
        llm=get_llm(),
    )


