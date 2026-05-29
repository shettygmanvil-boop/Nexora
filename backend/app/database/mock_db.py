"""
Mock Database for Maproom

Provides curated travel data for prototype locations:
- Bangalore (urban tourism, nightlife, workcation, cafes)
- Goa (beaches, nightlife, adventure, coastal tourism)
- Srinagar (cold weather, mountain tourism, scenic travel)
- Jaipur (heritage tourism, temples, cultural experiences)
"""

from typing import Optional

DESTINATIONS = {
    "bangalore": {
        "name": "Bangalore",
        "description": "The Silicon Valley of India, known for its pleasant weather, vibrant café culture, and beautiful gardens.",
        "vibes": ["urban", "nightlife", "workcation", "cafes", "technology", "gardens"],
        "weather_profile": {
            "average_temp": "24°C",
            "pollution_index": "Moderate (AQI 85)",
            "humidity": "50%",
            "general_condition": "Pleasant",
            "health_warnings": []
        },
        "hotels": [
            {
                "name": "Sleek Stay Indiranagar",
                "tier": "budget",
                "price_per_night": 2500,
                "rating": 4.2,
                "amenities": ["Wi-Fi", "AC", "Breakfast Included"],
                "reviews": ["Perfect for workcation", "Great location, clean rooms", "A bit noisy on weekends"]
            },
            {
                "name": "The Gardenia Retreat",
                "tier": "standard",
                "price_per_night": 5500,
                "rating": 4.5,
                "amenities": ["Wi-Fi", "AC", "Pool", "Gym", "Restaurant"],
                "reviews": ["Beautiful garden view", "Very polite staff", "Value for money"]
            },
            {
                "name": "The Leela Palace Bangalore",
                "tier": "luxury",
                "price_per_night": 15000,
                "rating": 4.9,
                "amenities": ["Spa", "Infinite Pool", "Fine Dining", "Lounge", "Valet Parking"],
                "reviews": ["Absolute luxury", "Royal treatment", "Exceeded expectations in hospitality"]
            }
        ],
        "attractions": [
            {"name": "Lalbagh Botanical Garden", "vibe": "relaxation", "fatigue_index": 2, "cost": 50, "description": "Lush green space featuring an iconic glass house."},
            {"name": "Indiranagar Cafe Hopping", "vibe": "cafes", "fatigue_index": 1, "cost": 1000, "description": "Explore the trendiest microbreweries and specialty coffee houses."},
            {"name": "Bangalore Palace", "vibe": "heritage", "fatigue_index": 3, "cost": 500, "description": "Royal palace exhibiting majestic architecture."},
            {"name": "Cubbon Park Walk", "vibe": "relaxation", "fatigue_index": 2, "cost": 0, "description": "Serene park walks ideal for senior citizens."}
        ]
    },
    "goa": {
        "name": "Goa",
        "description": "Famous for its sunny beaches, happening nightlife, historic Portuguese churches, and delicious seafood.",
        "vibes": ["beaches", "nightlife", "adventure", "coastal", "seafood", "relaxation"],
        "weather_profile": {
            "average_temp": "31°C",
            "pollution_index": "Good (AQI 35)",
            "humidity": "80%",
            "general_condition": "Warm & Humid",
            "health_warnings": ["High heat index. Ensure hydration for elderly and children."]
        },
        "hotels": [
            {
                "name": "Backpacker Hostel Anjuna",
                "tier": "budget",
                "price_per_night": 1200,
                "rating": 4.1,
                "amenities": ["Wi-Fi", "Common Room", "Bicycle Rental"],
                "reviews": ["Super friendly vibe", "Steps away from beach", "Great for solo travelers"]
            },
            {
                "name": "Calangute Beachside Inn",
                "tier": "standard",
                "price_per_night": 4500,
                "rating": 4.4,
                "amenities": ["Wi-Fi", "AC", "Pool", "Restaurant"],
                "reviews": ["Very family-friendly", "Direct beach access", "Nice pool"]
            },
            {
                "name": "Taj Exotica Resort & Spa",
                "tier": "luxury",
                "price_per_night": 18000,
                "rating": 4.8,
                "amenities": ["Private Beach", "Golf Course", "Spa", "Kids Club", "Fine Dining"],
                "reviews": ["Breathtaking sunset views", "Perfect luxury getaway", "Outstanding buffet spread"]
            }
        ],
        "attractions": [
            {"name": "Anjuna Beach Sunset & Night Market", "vibe": "nightlife", "fatigue_index": 3, "cost": 200, "description": "Vibrant beachside shopping and musical vibes."},
            {"name": "Scuba Diving at Grande Island", "vibe": "adventure", "fatigue_index": 5, "cost": 3000, "description": "Thrilling underwater exploration of marine life."},
            {"name": "Basilica of Bom Jesus", "vibe": "heritage", "fatigue_index": 2, "cost": 0, "description": "UNESCO World Heritage Site with classical Portuguese architecture."},
            {"name": "Dudhsagar Waterfalls Trek", "vibe": "adventure", "fatigue_index": 5, "cost": 1500, "description": "Four-tiered waterfall trek through deep jungle."}
        ]
    },
    "srinagar": {
        "name": "Srinagar",
        "description": "The summer capital of Jammu and Kashmir, celebrated for its houseboats, lakes, and Mughal gardens.",
        "vibes": ["cold", "mountains", "scenic", "spirituality", "nature", "relaxation"],
        "weather_profile": {
            "average_temp": "8°C",
            "pollution_index": "Good (AQI 42)",
            "humidity": "60%",
            "general_condition": "Cold",
            "health_warnings": ["Cold weather risk. Senior citizens and asthma patients should carry warm clothing and inhalers."]
        },
        "hotels": [
            {
                "name": "Dal Lake Budget Houseboat",
                "tier": "budget",
                "price_per_night": 2000,
                "rating": 4.0,
                "amenities": ["Wi-Fi", "Hot Water", "Shikara Ride Support"],
                "reviews": ["Unique experience", "Friendly host", "Basic but charming"]
            },
            {
                "name": "Shalimar Pine Resort",
                "tier": "standard",
                "price_per_night": 6000,
                "rating": 4.5,
                "amenities": ["Wi-Fi", "Heating", "Restaurant", "Garden"],
                "reviews": ["Splendid mountain views", "Very warm hospitality", "Great local Wazwan food"]
            },
            {
                "name": "The Khyber Himalayan Resort & Spa",
                "tier": "luxury",
                "price_per_night": 22000,
                "rating": 4.9,
                "amenities": ["Heated Indoor Pool", "Luxury Spa", "Snow View Balcony", "Ski Concierge"],
                "reviews": ["Heaven on Earth", "Unforgettable snowy landscape", "Premium service quality"]
            }
        ],
        "attractions": [
            {"name": "Shikara Ride on Dal Lake", "vibe": "relaxation", "fatigue_index": 1, "cost": 800, "description": "Tranquil wooden boat ride along floating gardens."},
            {"name": "Shalimar Bagh & Nishat Bagh", "vibe": "heritage", "fatigue_index": 2, "cost": 50, "description": "Terraced lawns and cascading fountains built by Mughal Emperors."},
            {"name": "Gulmarg Gondola Ride", "vibe": "adventure", "fatigue_index": 3, "cost": 900, "description": "High-altitude cable car offering sweeping snowy panorama."},
            {"name": "Hazratbal Shrine Visit", "vibe": "spirituality", "fatigue_index": 1, "cost": 0, "description": "A historic, serene place of worship beside Dal Lake."}
        ]
    },
    "jaipur": {
        "name": "Jaipur",
        "description": "The Pink City of India, rich in royal history, colossal forts, and vibrant textile bazaars.",
        "vibes": ["heritage", "temples", "culture", "shopping", "photography", "history"],
        "weather_profile": {
            "average_temp": "38°C",
            "pollution_index": "Moderate (AQI 110)",
            "humidity": "30%",
            "general_condition": "Hot & Dry",
            "health_warnings": ["Extreme heat warning. Avoid afternoon walking; suitable for morning/evening excursions."]
        },
        "hotels": [
            {
                "name": "Johari Palace Heritage Stay",
                "tier": "budget",
                "price_per_night": 1800,
                "rating": 4.2,
                "amenities": ["Wi-Fi", "AC", "Traditional Decor"],
                "reviews": ["Quaint and historic feel", "Very affordable", "Located close to Hawa Mahal"]
            },
            {
                "name": "Rajputana Haveli Hotel",
                "tier": "standard",
                "price_per_night": 5000,
                "rating": 4.6,
                "amenities": ["Wi-Fi", "AC", "Rooftop Restaurant", "Pool"],
                "reviews": ["Fabulous folk dance performances", "Awesome food", "Clean pool"]
            },
            {
                "name": "Rambagh Palace Jaipur",
                "tier": "luxury",
                "price_per_night": 25000,
                "rating": 4.9,
                "amenities": ["Royal Gardens", "Historic Suites", "Spa", "Vintage Cars Tour"],
                "reviews": ["Living like a King", "Incomparable palace experience", "Magical hospitality"]
            }
        ],
        "attractions": [
            {"name": "Amber Fort Elephant/Jeep Tour", "vibe": "heritage", "fatigue_index": 4, "cost": 600, "description": "Hilltop fort with artistic gateways and mirror halls."},
            {"name": "Hawa Mahal & Old City Street Walk", "vibe": "photography", "fatigue_index": 3, "cost": 100, "description": "Intricate honeycomb window facade, great for photo shoots."},
            {"name": "Birla Mandir Temple", "vibe": "temples", "fatigue_index": 1, "cost": 0, "description": "White marble temple peaceful for elderly family members."},
            {"name": "Chokhi Dhani Ethnic Resort Village", "vibe": "culture", "fatigue_index": 3, "cost": 1200, "description": "Cultural hub with folk dances, camel rides, and local dining."}
        ]
    }
}

def get_destination(dest_name: str) -> Optional[dict]:
    """Retrieve details for a specific destination name."""
    return DESTINATIONS.get(dest_name.lower())

def list_destinations() -> list:
    """Return list of all supported destinations."""
    return list(DESTINATIONS.keys())
