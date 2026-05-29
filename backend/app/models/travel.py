from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class TravelerProfile(BaseModel):
    """
    Profile representing an individual traveler within a group.
    """
    name: str = Field(..., description="Name of the traveler")
    age: int = Field(..., description="Age of the traveler")
    medical_conditions: List[str] = Field(default_factory=list, description="Medical illnesses or health concerns (e.g., asthma, knee pain)")
    vibe_preference: str = Field(..., description="Vibe preferred (e.g., beaches, heritage, cafes, nightlife, spirituality, nature)")
    accommodation_preference: str = Field(default="standard", description="Accommodation tier preference (budget, standard, luxury)")
    travel_style: str = Field(default="relaxation", description="Preferred travel style (relaxation, adventure, photography, workcation, digital detox)")
    travel_purpose: str = Field(default="leisure", description="Travel purpose (relaxation, adventure, spirituality, luxury, family bonding, workcation, photography, digital detox)")
    food_preference: str = Field(default="veg", description="Food taste / preference (veg, non-veg, vegan)")

class TravelGroupRequest(BaseModel):
    """
    Request model for travel recommendation.
    """
    travelers: List[TravelerProfile] = Field(..., description="List of travelers in the group")
    total_budget: Optional[float] = Field(None, description="Total combined travel budget in INR")
    num_days: Optional[int] = Field(3, description="Number of days of stay")
    expectations: str = Field("", description="Expectation statement, e.g., 'I want a peaceful lake with less crowd and sunset views.'")
    destination_preference: Optional[str] = Field(None, description="Optional chosen location name (e.g., Goa, Bangalore, Srinagar, Jaipur). Leave empty if confused.")
    hotel_count: int = Field(default=3, description="Number of hotel recommendations to return, between 3 and 10", ge=3, le=10)
    priorities: List[str] = Field(default_factory=list, description="Ordered priorities of the user")

class ItineraryActivity(BaseModel):
    """
    Activity details inside an itinerary.
    """
    time: str = Field(..., description="Time of the activity (e.g., Morning, Afternoon, Evening)")
    activity_name: str = Field(..., description="Name of the attraction or activity")
    description: str = Field(..., description="Description of the activity")
    estimated_cost: float = Field(..., description="Cost of the activity in INR")
    fatigue_level: int = Field(..., description="Fatigue rating from 1 to 5")
    assigned_to: List[str] = Field(default_factory=list, description="Who is performing this activity (e.g. specific traveler names, or 'All')")

class ItineraryDay(BaseModel):
    """
    Single day schedule of the itinerary.
    """
    day: int = Field(..., description="Day number")
    activities: List[ItineraryActivity] = Field(..., description="List of activities scheduled for the day")

class BudgetAllocation(BaseModel):
    """
    Details of how budget is distributed.
    """
    accommodation_cost: float = Field(..., description="Estimated cost for hotels")
    activities_cost: float = Field(..., description="Estimated cost for sightseeing/activities")
    buffer_amount: float = Field(..., description="Emergency buffer amount")
    remaining_balance: float = Field(..., description="Leftover budget")
    explanation: str = Field(..., description="Explanation of why this allocation makes sense")

class MatchScoreDetail(BaseModel):
    """
    Expectation vs Reality alignment.
    """
    score: int = Field(..., description="Match score out of 100")
    matching_aspects: List[str] = Field(..., description="List of aspects that match expectations")
    deviating_aspects: List[str] = Field(..., description="List of aspects that do not match expectations")
    reality_check_summary: str = Field(..., description="Summary explaining destination reality vs expectations")

class WeatherSafetyDetail(BaseModel):
    """
    Weather risks and safety details for travelers.
    """
    general_condition: str = Field(..., description="General weather forecast summary")
    health_warnings: List[str] = Field(..., description="Crucial medical alerts based on traveler conditions")
    alternative_indoor_activities: List[str] = Field(..., description="Suggested indoor changes in case of weather/health risks")

class SimulationResponse(BaseModel):
    """
    Dynamic simulation response after slider updates.
    """
    updated_budget_allocation: BudgetAllocation
    suggested_upgrades: List[str]
    compatibility_score: float
    itinerary_changes: List[str]

class HotelRecommendation(BaseModel):
    """
    Represents hotel or restaurant recommendation details with review sentiments.
    """
    name: str = Field(..., description="Name of the hotel or restaurant")
    price_per_night: float = Field(..., description="Price per night or cost per head in INR")
    rating: float = Field(..., description="Rating out of 5")
    amenities: List[str] = Field(default_factory=list, description="Key amenities offered")
    reviews: List[str] = Field(default_factory=list, description="Snippet of reviews")
    specialty_keyword: str = Field(..., description="A keyword highlighting the specialty (e.g. Value for Money)")

class RecommendationResponse(BaseModel):
    """
    Ultimate structured output of Maproom's Multi-Agent Recommendation System.
    """
    destination_name: str = Field(..., description="Recommended destination")
    description: str = Field(..., description="Brief description of the recommended place")
    group_compatibility_score: float = Field(..., description="Calculated percentage compatibility for the group")
    group_itinerary: List[ItineraryDay] = Field(..., description="Activities that the entire group does together")
    solo_itineraries: Dict[str, List[ItineraryDay]] = Field(..., description="Custom sub-itineraries for specific members/sub-groups")
    reunion_schedule: List[ItineraryDay] = Field(..., description="Schedule for reunions, meals, and regrouping activities")
    conflict_resolution_summary: str = Field(..., description="Details on how the system resolved preference clashes")
    budget_analysis: BudgetAllocation = Field(..., description="Detailed breakdown of budget distribution")
    weather_health_safety: WeatherSafetyDetail = Field(..., description="Medical alerts and climate analysis")
    expectation_reality_match: MatchScoreDetail = Field(..., description="Score and justification matching user's written expectations")
    explainable_ai_reasons: List[str] = Field(..., description="Bullet points explaining why this plan is optimized for the group")
    smart_budget_expansions: List[str] = Field(..., description="Upsell suggestions detailing what slightly more budget would unlock")
    hotels: List[HotelRecommendation] = Field(default_factory=list, description="Recommended hotel options (3 to 10)")
