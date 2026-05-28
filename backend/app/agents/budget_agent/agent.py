from crewai import Agent
from app.agents.budget_agent.prompts import BUDGET_SYSTEM_PROMPT

budget_optimization_agent = Agent(
    role="AI Budget Optimization Agent",
    goal="Maximize travel value within group budget constraints, handle real-time slider updates, and identify smart expansion opportunities.",
    backstory=BUDGET_SYSTEM_PROMPT,
    verbose=True,
    allow_delegation=False
)
