try:
    from crewai import Agent
    CREWAI_AVAILABLE = True
except ImportError:
    Agent = None
    CREWAI_AVAILABLE = False

from backend.utils.config import settings
from backend.prompts import agent_prompts

def get_llm():
    """
    Instantiates and returns the configured LLM based on settings.
    Returns None if provider is 'mock' or keys are missing.
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "openai" and settings.OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.LLM_MODEL_NAME,
                api_key=settings.OPENAI_API_KEY
            )
        except ImportError:
            pass
            
    elif provider == "gemini" and settings.GEMINI_API_KEY:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL_NAME,
                google_api_key=settings.GEMINI_API_KEY
            )
        except ImportError:
            pass
            
    return None

def create_preference_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed. Please install dependencies in requirements.txt on a supported Python version.")
    return Agent(
        role=agent_prompts.PREFERENCE_ANALYSIS_ROLE,
        goal="Analyze traveler demographics, vibes, and preferences to find common ground and conflicts.",
        backstory=agent_prompts.PREFERENCE_ANALYSIS_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def create_budget_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed.")
    return Agent(
        role=agent_prompts.BUDGET_OPTIMIZER_ROLE,
        goal="Allocate budget efficiently between hotel tier, activities, and food, and generate smart budget expansion suggestions.",
        backstory=agent_prompts.BUDGET_OPTIMIZER_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def create_weather_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed.")
    return Agent(
        role=agent_prompts.WEATHER_HEALTH_ROLE,
        goal="Evaluate weather suitability, air quality, temperature comfort, and match with traveler health conditions.",
        backstory=agent_prompts.WEATHER_HEALTH_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def create_accommodation_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed.")
    return Agent(
        role=agent_prompts.ACCOMMODATION_INTEL_ROLE,
        goal="Select optimal lodging options and analyze guest reviews to highlight suitability.",
        backstory=agent_prompts.ACCOMMODATION_INTEL_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def create_itinerary_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed.")
    return Agent(
        role=agent_prompts.ITINERARY_PLANNER_ROLE,
        goal="Create daily schedules that optimize route flow, travel times, and minimize physical fatigue.",
        backstory=agent_prompts.ITINERARY_PLANNER_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def create_conflict_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed.")
    return Agent(
        role=agent_prompts.CONFLICT_RESOLVER_ROLE,
        goal="Resolve schedule conflicts by scheduling group reunions and custom split solo itineraries.",
        backstory=agent_prompts.CONFLICT_RESOLVER_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=True
    )

def create_expectation_agent(llm) -> "Agent":
    if Agent is None:
        raise RuntimeError("CrewAI is not installed.")
    return Agent(
        role=agent_prompts.EXPECTATION_ANALYSIS_ROLE,
        goal="Determine how closely a destination matches a user's expectations using real-world characteristics.",
        backstory=agent_prompts.EXPECTATION_ANALYSIS_BACKSTORY,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
