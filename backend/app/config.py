"""
Centralized Configuration
=========================
Loads environment variables and exposes a shared LLM instance
used across all CrewAI agents in the Maproom platform.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import LLM

# Load environment variables from the project root .env file
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Explicitly bind to the correct stable model version via Google GenAI.
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

langchain_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=api_key,
)

# Shared LLM wrapper for CrewAI agents
shared_llm = LLM(
    model="gemini/gemini-2.5-flash",
    custom_llm=langchain_gemini
)

