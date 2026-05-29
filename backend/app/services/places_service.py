import requests
from typing import List, Dict, Any, Optional
from app.config import settings
from app.database import mock_db

def get_live_hotels(destination: str, tier: str = "standard", limit: int = 5) -> List[Dict[str, Any]]:
    """
    Query Google Places API for hotels in the given destination matching the preferred tier.
    Falls back to mock_db if key is missing, invalid, or query fails.
    """
    dest_key = destination.strip().lower()
    local_hotels = mock_db.DESTINATIONS.get(dest_key, mock_db.DESTINATIONS["goa"]).get("hotels", [])

    api_key = settings.google_maps_api_key
    if not api_key:
        # Fall back to local mock data
        return local_hotels[:limit]

    try:
        # 1. Text Search for hotels of specific tier
        query_str = f"{tier} hotels in {destination}"
        search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query_str,
            "key": api_key
        }
        
        response = requests.get(search_url, params=params, timeout=5)
        if response.status_code != 200:
            return local_hotels[:limit]
            
        data = response.json()
        if data.get("status") != "OK":
            # e.g. REQUEST_DENIED or OVER_QUERY_LIMIT
            return local_hotels[:limit]

        results = data.get("results", [])[:limit]
        hotels_list = []

        for item in results:
            place_id = item.get("place_id")
            name = item.get("name", "Unknown Hotel")
            rating = item.get("rating", 4.0)
            price_level = item.get("price_level", 2)
            
            # Map price level to simulated INR costs per night
            # $ = 1500, $$ = 3500, $$$ = 7500, $$$$ = 15000
            price_estimates = {0: 1200, 1: 1800, 2: 3800, 3: 8500, 4: 16000}
            price_per_night = price_estimates.get(price_level, 3500)
            
            # Default amenities and reviews
            amenities = ["Free WiFi", "AC", "Room Service"]
            reviews = [f"Great stay at {name}. Clean rooms and helpful staff."]
            specialty_keyword = "Value for Money"

            # 2. Call Place Details API to get actual reviews & amenities if possible
            if place_id:
                try:
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    details_params = {
                        "place_id": place_id,
                        "fields": "reviews,editorial_summary,types,price_level",
                        "key": api_key
                    }
                    d_res = requests.get(details_url, params=details_params, timeout=3)
                    if d_res.status_code == 200:
                        d_data = d_res.json().get("result", {})
                        
                        # Extract reviews
                        api_reviews = d_data.get("reviews", [])
                        if api_reviews:
                            reviews = [r.get("text", "") for r in api_reviews if r.get("text")][:2]
                            
                        # Adjust price level if details returns it
                        det_price = d_data.get("price_level")
                        if det_price is not None:
                            price_per_night = price_estimates.get(det_price, price_per_night)
                            
                        # Extract specialty based on ratings/types
                        types = d_data.get("types", [])
                        if rating >= 4.5:
                            specialty_keyword = "Highly Rated"
                        elif "spa" in types or "resort" in name.lower():
                            specialty_keyword = "Luxury Resort Vibe"
                        elif price_level <= 1:
                            specialty_keyword = "Budget Friendly"
                            
                        # Add amenities based on details summary or names
                        if "spa" in types:
                            amenities.append("Spa services")
                        if "pool" in name.lower() or "resort" in name.lower():
                            amenities.append("Swimming Pool")
                        if "restaurant" in types:
                            amenities.append("Restaurant")
                except Exception:
                    pass  # keep default reviews/amenities on exception

            hotels_list.append({
                "name": name,
                "price_per_night": price_per_night,
                "rating": rating,
                "tier": tier,
                "specialty_keyword": specialty_keyword,
                "amenities": list(set(amenities)),
                "reviews": reviews
            })
            
        if not hotels_list:
            return local_hotels[:limit]
        return hotels_list
        
    except Exception:
        return local_hotels[:limit]


def get_live_attractions(destination: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Query Google Places API for tourist attractions in the given destination.
    Falls back to mock_db if key is missing, invalid, or query fails.
    """
    dest_key = destination.strip().lower()
    local_attractions = mock_db.DESTINATIONS.get(dest_key, mock_db.DESTINATIONS["goa"]).get("attractions", [])

    api_key = settings.google_maps_api_key
    if not api_key:
        return local_attractions[:limit]

    try:
        query_str = f"top tourist attractions, amusement parks, and places to visit in {destination}"
        search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query_str,
            "key": api_key
        }
        
        response = requests.get(search_url, params=params, timeout=5)
        if response.status_code != 200:
            return local_attractions[:limit]
            
        data = response.json()
        if data.get("status") != "OK":
            return local_attractions[:limit]

        results = data.get("results", [])[:limit]
        attractions_list = []

        for idx, item in enumerate(results):
            name = item.get("name", "Local Attraction")
            rating = item.get("rating", 4.0)
            
            # Map rating/popularity to dynamic fatigue indexing (1-5) and simulated ticket cost (INR)
            fatigue_index = 2
            if idx % 3 == 0:
                fatigue_index = 3
            elif idx % 4 == 0:
                fatigue_index = 4
                
            cost_estimates = [0, 150, 300, 500, 800]
            cost = cost_estimates[idx % len(cost_estimates)]
            
            # Generate a realistic description using the details/name
            formatted_address = item.get("formatted_address", "")
            description = f"Popular tourist destination located at {formatted_address}. Rating: {rating} stars."

            attractions_list.append({
                "name": name,
                "vibe": "scenic" if idx % 2 == 0 else "heritage",
                "fatigue_index": fatigue_index,
                "cost": cost,
                "description": description
            })
            
        if not attractions_list:
            return local_attractions[:limit]
        return attractions_list
        
    except Exception:
        return local_attractions[:limit]
