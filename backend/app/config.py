"""
Centralized Configuration
=========================
Loads environment variables and exposes a shared LLM instance
used across all CrewAI agents in the Maproom platform.
"""

from crewai import LLM

# ---------------------------------------------------------------------------
# LLM Configuration
# ---------------------------------------------------------------------------
# Shared Gemini LLM instance used by all CrewAI agents.
# ---------------------------------------------------------------------------

llm = LLM(
    model="gemini/gemini-pro",
    api_key="AIzaSyDo1kOidZdeDMPBs6QYpEXuP-38EOv3XZQ",
)
