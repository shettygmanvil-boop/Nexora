"""
Destination Database for Maproom

Provides structured destination details for:
- Goa
- Bangalore
- Srinagar
- Jaipur

Includes helper functions for querying data.
"""

from typing import List, Dict, Any, Optional

# Structured Destination Dataset
DESTINATIONS: Dict[str, Dict[str, Any]] = {
    "goa": {
        "name": "Goa",
        "nightlife_score": 9,
        "peacefulness_score": 5,
        "adventure_score": 8,
        "luxury_score": 7,
        "family_friendliness": 7,
        "crowd_level": "High",
        "weather_type": "Warm & Humid",
        "veg_food_availability": "Medium",
        "senior_citizen_friendliness": 5,
        "budget_friendliness": 7,
        "best_for": "Beach parties, water sports, and historical architecture",
        "medical_risk_notes": "Dehydration risk under high heat index. Ensure hydration for elderly and children.",
        "top_activities": [
            "Scuba Diving at Grande Island",
            "Anjuna Beach Sunset & Night Market",
            "Basilica of Bom Jesus Visit",
            "Dudhsagar Waterfalls Trek"
        ],
        "vibes": ["beaches", "nightlife", "adventure", "coastal", "relaxation"]
    },
    "bangalore": {
        "name": "Bangalore",
        "nightlife_score": 8,
        "peacefulness_score": 6,
        "adventure_score": 5,
        "luxury_score": 8,
        "family_friendliness": 8,
        "crowd_level": "High",
        "weather_type": "Pleasant",
        "veg_food_availability": "High",
        "senior_citizen_friendliness": 8,
        "budget_friendliness": 6,
        "best_for": "Cafe culture, tech hubs, microbreweries, and beautiful gardens",
        "medical_risk_notes": "Moderate pollution levels. Asthma patients should check current AQI status.",
        "top_activities": [
            "Lalbagh Botanical Garden walk",
            "Indiranagar Cafe Hopping",
            "Bangalore Palace Tour",
            "Cubbon Park Walk"
        ],
        "vibes": ["urban", "nightlife", "workcation", "cafes", "technology", "gardens"]
    },
    "srinagar": {
        "name": "Srinagar",
        "nightlife_score": 2,
        "peacefulness_score": 9,
        "adventure_score": 7,
        "luxury_score": 8,
        "family_friendliness": 9,
        "crowd_level": "Medium",
        "weather_type": "Cold",
        "veg_food_availability": "Medium",
        "senior_citizen_friendliness": 7,
        "budget_friendliness": 5,
        "best_for": "Scenic lake houseboats, mountain views, and quiet gardens",
        "medical_risk_notes": "Cold weather and high altitude risk. Asthma and heart patients should carry warm wear and inhalers.",
        "top_activities": [
            "Shikara Ride on Dal Lake",
            "Gulmarg Gondola Ride",
            "Shalimar Bagh Stroll",
            "Hazratbal Shrine Visit"
        ],
        "vibes": ["cold", "mountains", "scenic", "spirituality", "nature", "relaxation"]
    },
    "jaipur": {
        "name": "Jaipur",
        "nightlife_score": 5,
        "peacefulness_score": 7,
        "adventure_score": 6,
        "luxury_score": 9,
        "family_friendliness": 9,
        "crowd_level": "High",
        "weather_type": "Hot & Dry",
        "veg_food_availability": "High",
        "senior_citizen_friendliness": 8,
        "budget_friendliness": 7,
        "best_for": "Royal heritage, palaces, temples, and cultural experiences",
        "medical_risk_notes": "Extreme afternoon heat. Stay hydrated and avoid outdoor walking during mid-day peak heat.",
        "top_activities": [
            "Amber Fort Elephant/Jeep Tour",
            "Hawa Mahal Photography Walk",
            "Birla Mandir Temple Visit",
            "Chokhi Dhani Ethnic Resort Village Dinner"
        ],
        "vibes": ["heritage", "temples", "culture", "shopping", "photography", "history"]
    }
}


def get_all_destinations() -> List[Dict[str, Any]]:
    """
    Retrieve all structured destinations.
    
    Returns:
        List[Dict[str, Any]]: List of all destination data dictionaries.
    """
    try:
        return list(DESTINATIONS.values())
    except Exception as e:
        # Generic safety error wrapper
        raise RuntimeError(f"Failed to retrieve destinations from database: {str(e)}")


def get_destination_by_name(name: str) -> Dict[str, Any]:
    """
    Retrieve a destination details by name (case-insensitive).
    
    Args:
        name (str): Name of the destination (e.g. 'Goa')
        
    Returns:
        Dict[str, Any]: Destination data dictionary.
        
    Raises:
        ValueError: If destination name is empty or not found in the database.
    """
    if not name or not name.strip():
        raise ValueError("Destination name cannot be empty")
        
    key = name.strip().lower()
    if key not in DESTINATIONS:
        raise ValueError(f"Destination '{name}' not found in the database. Supported: {', '.join(DESTINATIONS.keys())}")
        
    return DESTINATIONS[key]


def get_destinations_by_vibe(vibe: str) -> List[Dict[str, Any]]:
    """
    Filter and retrieve destinations that match a specific vibe (case-insensitive).
    
    A match occurs if the vibe is explicitly listed in the destination's 'vibes' list,
    or if it aligns with a high score (>= 7) for a related feature category.
    
    Args:
        vibe (str): Vibe keyword (e.g. 'beaches', 'nightlife', 'nature')
        
    Returns:
        List[Dict[str, Any]]: List of matching destination dictionaries.
        
    Raises:
        ValueError: If the vibe query parameter is empty.
    """
    if not vibe or not vibe.strip():
        raise ValueError("Vibe query parameter cannot be empty")
        
    vibe_query = vibe.strip().lower()
    matching_destinations = []
    
    for dest in DESTINATIONS.values():
        # Check explicit vibes list
        if vibe_query in dest.get("vibes", []):
            matching_destinations.append(dest)
            continue
            
        # Fallback to feature scores if applicable (threshold of >= 7 out of 10 represents a high score)
        if vibe_query == "nightlife" and dest.get("nightlife_score", 0) >= 7:
            matching_destinations.append(dest)
        elif vibe_query in ["peaceful", "peacefulness", "relaxation"] and dest.get("peacefulness_score", 0) >= 7:
            matching_destinations.append(dest)
        elif vibe_query == "adventure" and dest.get("adventure_score", 0) >= 7:
            matching_destinations.append(dest)
        elif vibe_query == "luxury" and dest.get("luxury_score", 0) >= 7:
            matching_destinations.append(dest)
        elif vibe_query in ["family", "family_friendly"] and dest.get("family_friendliness", 0) >= 7:
            matching_destinations.append(dest)
        elif vibe_query in ["senior", "elderly"] and dest.get("senior_citizen_friendliness", 0) >= 7:
            matching_destinations.append(dest)
        elif vibe_query in ["budget", "cheap"] and dest.get("budget_friendliness", 0) >= 7:
            matching_destinations.append(dest)
            
    return matching_destinations
