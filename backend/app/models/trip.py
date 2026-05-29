from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class Traveler(BaseModel):
    """
    Model representing an individual traveler and their preferences.
    """
    name: str = Field(
        ..., 
        description="Name of the traveler",
        min_length=1
    )
    age: int = Field(
        ..., 
        description="Age of the traveler in years",
        ge=0,
        le=120
    )
    food_preference: str = Field(
        default="veg", 
        description="Food preference, e.g. 'veg', 'non-veg', 'vegan', 'halal', 'kosher'"
    )
    mood: str = Field(
        default="excited", 
        description="Current mood or vibe of the traveler, e.g. 'relaxed', 'adventurous', 'chill', 'excited'"
    )
    travel_purpose: str = Field(
        default="leisure", 
        description="Primary purpose of travel, e.g. 'leisure', 'adventure', 'business', 'nature exploration'"
    )
    medical_conditions: List[str] = Field(
        default_factory=list, 
        description="List of medical conditions (e.g. 'asthma', 'diabetes', 'hypertension')"
    )
    activity_level: str = Field(
        default="medium", 
        description="Preferred activity intensity: 'low', 'medium', or 'high'"
    )
    budget_preference: str = Field(
        default="standard", 
        description="Budget tier preference: 'budget', 'standard', or 'luxury'"
    )

    @field_validator("activity_level")
    @classmethod
    def validate_activity_level(cls, v: str) -> str:
        v_lower = v.strip().lower()
        allowed = {"low", "medium", "high"}
        if v_lower not in allowed:
            raise ValueError(f"activity_level must be one of {allowed}")
        return v_lower

    @field_validator("budget_preference")
    @classmethod
    def validate_budget_preference(cls, v: str) -> str:
        v_lower = v.strip().lower()
        allowed = {"budget", "standard", "luxury"}
        if v_lower not in allowed:
            raise ValueError(f"budget_preference must be one of {allowed}")
        return v_lower

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Jane Doe",
                "age": 29,
                "food_preference": "veg",
                "mood": "adventurous",
                "travel_purpose": "leisure",
                "medical_conditions": ["asthma"],
                "activity_level": "high",
                "budget_preference": "standard"
            }
        }
    }


class GroupTripRequest(BaseModel):
    """
    Model representing a group trip planning request.
    """
    travelers: List[Traveler] = Field(
        ..., 
        description="List of travelers participating in the trip"
    )
    budget: float = Field(
        ..., 
        description="Total combined trip budget in INR",
        gt=0
    )
    days: int = Field(
        ..., 
        description="Duration of the trip in days",
        gt=0
    )
    preferred_vibe: str = Field(
        ..., 
        description="Preferred vibe of the destination, e.g. 'beaches', 'mountains', 'nightlife', 'heritage'"
    )
    priorities: List[str] = Field(
        ..., 
        description="List of group priorities, e.g. ['sightseeing', 'party', 'relaxation', 'food']"
    )
    destination_preference: Optional[str] = Field(
        default=None, 
        description="Optional preferred destination name, e.g. 'Goa', 'Bangalore'"
    )
    expectations: Optional[str] = Field(
        default="", 
        description="Optional written expectations or desires for the trip"
    )

    @field_validator("travelers")
    @classmethod
    def validate_travelers_not_empty(cls, v: List[Traveler]) -> List[Traveler]:
        if not v:
            raise ValueError("The travelers list must contain at least one traveler.")
        return v

    @field_validator("priorities")
    @classmethod
    def validate_priorities_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("The priorities list must contain at least one priority.")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "travelers": [
                    {
                        "name": "Alice",
                        "age": 28,
                        "food_preference": "veg",
                        "mood": "excited",
                        "travel_purpose": "leisure",
                        "medical_conditions": [],
                        "activity_level": "medium",
                        "budget_preference": "standard"
                    },
                    {
                        "name": "Bob",
                        "age": 65,
                        "food_preference": "non-veg",
                        "mood": "relaxed",
                        "travel_purpose": "relaxation",
                        "medical_conditions": ["hypertension"],
                        "activity_level": "low",
                        "budget_preference": "luxury"
                    }
                ],
                "budget": 50000.0,
                "days": 4,
                "preferred_vibe": "beaches",
                "priorities": ["relaxation", "sightseeing"],
                "destination_preference": "Goa",
                "expectations": "I want a relaxing beach getaway with beautiful sunset views and good vegetarian food."
            }
        }
    }


class DestinationDetail(BaseModel):
    """
    Model representing detailed characteristics of a destination.
    """
    name: str = Field(..., description="Name of the destination")
    nightlife_score: int = Field(..., description="Nightlife score out of 10", ge=1, le=10)
    peacefulness_score: int = Field(..., description="Peacefulness score out of 10", ge=1, le=10)
    adventure_score: int = Field(..., description="Adventure score out of 10", ge=1, le=10)
    luxury_score: int = Field(..., description="Luxury score out of 10", ge=1, le=10)
    family_friendliness: int = Field(..., description="Family friendliness score out of 10", ge=1, le=10)
    crowd_level: str = Field(..., description="Crowd level, e.g. 'Low', 'Medium', 'High'")
    weather_type: str = Field(..., description="Weather type, e.g. 'Cold', 'Pleasant', 'Hot & Dry', 'Warm & Humid'")
    veg_food_availability: str = Field(..., description="Availability of vegetarian food: 'Low', 'Medium', 'High'")
    senior_citizen_friendliness: int = Field(..., description="Senior citizen friendliness score out of 10", ge=1, le=10)
    budget_friendliness: int = Field(..., description="Budget friendliness score out of 10", ge=1, le=10)
    best_for: str = Field(..., description="Summary of what the destination is best suited for")
    medical_risk_notes: str = Field(..., description="Risk or warning notes regarding medical conditions at destination")
    top_activities: List[str] = Field(..., description="List of top attractions/activities at destination")
    vibes: List[str] = Field(default_factory=list, description="Vibes associated with the destination")

    model_config = {
        "json_schema_extra": {
            "example": {
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
                "top_activities": ["Scuba Diving at Grande Island", "Anjuna Beach Sunset Walk"],
                "vibes": ["beaches", "nightlife", "adventure", "coastal", "relaxation"]
            }
        }
    }


class RecommendationResponse(BaseModel):
    """
    Model representing the travel recommendation output response.
    """
    recommended_destination: str = Field(..., description="Name of the recommended destination")
    compatibility_score: float = Field(..., description="Overall group compatibility score out of 100")
    reasons: List[str] = Field(..., description="List of reasons for this recommendation")
    suggested_activities: List[str] = Field(..., description="Suggested activities matching traveler preferences")
    budget_summary: str = Field(..., description="Breakdown summary of the budget suitability")
    warnings: List[str] = Field(..., description="Safety and medical alert warnings for travelers")

    model_config = {
        "json_schema_extra": {
            "example": {
                "recommended_destination": "Goa",
                "compatibility_score": 88.5,
                "reasons": [
                    "Goa matches the requested 'beaches' vibe perfectly.",
                    "Goa offers high adventure activities matching Alice's interest.",
                    "Goa provides comfortable stays and good food options."
                ],
                "suggested_activities": [
                    "Scuba Diving at Grande Island",
                    "Anjuna Beach Sunset Walk"
                ],
                "budget_summary": "Total budget is ₹50,000 for 4 days (₹6,250/day per person). This is highly sufficient for standard hotels and activities.",
                "warnings": [
                    "Senior medical warning: Bob has hypertension. Goa has high humidity and heat; avoid midday outdoor activities."
                ]
            }
        }
    }


class ExpectationMatchResponse(BaseModel):
    """
    Model representing expectation vs reality match analysis.
    """
    match_percentage: float = Field(..., description="Expectation match percentage")
    summary: str = Field(..., description="Expectation analysis summary")


class RecommendationDetails(BaseModel):
    """
    Detailed recommendation schema for ranked destinations.
    """
    destination: str = Field(..., description="Name of the destination")
    compatibility_score: float = Field(..., description="Overall compatibility score out of 100")
    reasons: List[str] = Field(..., description="List of reasons for this recommendation")
    warnings: List[str] = Field(..., description="Safety and medical warnings for travelers")
    top_activities: List[str] = Field(..., description="Top attractions/activities at the destination")
    expectation_match: ExpectationMatchResponse = Field(..., description="Expectation vs reality match details")
    factor_scores: dict[str, float] = Field(..., description="Breakdown of individual factor scores")
    score_explanation: str = Field(..., description="Detailed explanation of the compatibility score")
