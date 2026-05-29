from app.utils.config import settings

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
                api_key=settings.OPENAI_API_KEY  # type: ignore
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
