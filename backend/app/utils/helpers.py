import re
import json
from typing import Any, Dict, List

def clean_json_output(text: str) -> str:
    """
    Cleans markdown code fences (like ```json ... ```) from the LLM output
    to extract raw JSON content.
    """
    if not text:
        return "{}"
    
    # Remove markdown code block if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text.strip()

def parse_json_safely(text: str) -> Dict[str, Any]:
    """
    Attempts to safely parse json from a string, cleaning it first.
    Returns empty dict on failure.
    """
    cleaned = clean_json_output(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}

def calculate_fatigue_index(activities: List[Dict[str, Any]]) -> float:
    """
    Calculates the average fatigue level of a list of activities.
    Fatigue level of activities is rated from 1 to 5.
    """
    if not activities:
        return 0.0
    total = sum(activity.get("fatigue_level", 2) for activity in activities)
    return round(total / len(activities), 1)

def calculate_compatibility(travelers: List[Any], destination_vibes: List[str]) -> float:
    """
    Calculates a basic compatibility score (0-100) based on how well the travelers' 
    vibe preferences match the destination's vibes.
    """
    if not travelers or not destination_vibes:
        return 50.0
        
    scores = []
    for t in travelers:
        # Pydantic model check
        vibe = getattr(t, "vibe_preference", "").lower()
        # Direct dictionary check fallback
        if not vibe and isinstance(t, dict):
            vibe = t.get("vibe_preference", "").lower()
            
        if vibe in destination_vibes:
            scores.append(100.0)
        else:
            # Partial match for similar categories
            scores.append(60.0)
            
    return round(sum(scores) / len(scores), 1)
