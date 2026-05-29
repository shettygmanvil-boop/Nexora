import json
from typing import List, Dict, Any, Optional

try:
    from crewai import Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    Crew = None
    Process = None
    CREWAI_AVAILABLE = False


from app.models.travel import (
    TravelGroupRequest, 
    RecommendationResponse, 
    BudgetAllocation, 
    MatchScoreDetail, 
    WeatherSafetyDetail, 
    ItineraryDay, 
    ItineraryActivity,
    HotelRecommendation
)
from app.database import mock_db
from app.config import settings
from app.utils.helpers import calculate_compatibility, parse_json_safely
from app.agents import travel_agents, travel_tasks
from app.services import places_service

def generate_mock_recommendation(request: TravelGroupRequest) -> RecommendationResponse:
    """
    Generates a high-quality simulated multi-agent travel recommendation response
    using rules and local mock database records.
    Runs instantly and avoids external API requirements.
    """
    num_days = request.num_days or 3
    
    # 1. Select destination
    dest_name = request.destination_preference
    if not dest_name or dest_name.lower() not in mock_db.DESTINATIONS:
        # Match based on vibes of travelers
        traveler_vibes = [t.vibe_preference.lower() for t in request.travelers]
        if any(v in ["beaches", "adventure", "coastal"] for v in traveler_vibes):
            dest_name = "goa"
        elif any(v in ["cold", "mountains", "scenic"] for v in traveler_vibes):
            dest_name = "srinagar"
        elif any(v in ["heritage", "temples", "spirituality"] for v in traveler_vibes):
            dest_name = "jaipur"
        else:
            dest_name = "bangalore"
            
    dest: Dict[str, Any] = mock_db.DESTINATIONS[dest_name.lower()]
    
    # 2. Budget Estimation if Optional
    total_budget = request.total_budget
    if not total_budget or total_budget <= 0:
        pref_tier = request.travelers[0].accommodation_preference.lower()
        if pref_tier == "luxury":
            est_cost = 12000
        elif pref_tier == "budget":
            est_cost = 2500
        else:
            est_cost = 6000
        total_budget = len(request.travelers) * num_days * est_cost
        
    # 3. Compatibility Score
    comp_score = calculate_compatibility(request.travelers, dest["vibes"])
    # Adjust score slightly based on priorities if present
    if request.priorities:
        if request.priorities[0].lower() == "vibe" and any(v in dest["vibes"] for v in [t.vibe_preference.lower() for t in request.travelers]):
            comp_score = min(100.0, comp_score + 5.0)
            
    # 4. Budget Analysis
    accom_cost = total_budget * 0.45
    activities_cost = total_budget * 0.35
    buffer_amt = total_budget * 0.10
    remaining = total_budget - (accom_cost + activities_cost + buffer_amt)
    
    budget_analysis = BudgetAllocation(
        accommodation_cost=round(accom_cost, 2),
        activities_cost=round(activities_cost, 2),
        buffer_amount=round(buffer_amt, 2),
        remaining_balance=round(remaining, 2),
        explanation=f"Allocated 45% for a {request.travelers[0].accommodation_preference} tier stay, 35% for group and individual sightseeing, and reserved a 10% emergency buffer."
    )
    
    # 5. Weather & Safety Warnings
    warnings = []
    alternative_indoors = [
        "Museum / Art Gallery visits",
        "Indoor local shopping emporiums",
        "Hotel spa or recreational games room"
    ]
    has_elderly = any(t.age >= 60 for t in request.travelers)
    has_asthma = any("asthma" in [m.lower() for m in t.medical_conditions] for t in request.travelers)
    has_knee_pain = any(any(k in m.lower() for k in ["knee", "mobility", "walking"]) for t in request.travelers for m in t.medical_conditions)
    
    weather_cond = dest["weather_profile"]["general_condition"]
    if dest_name.lower() == "srinagar" and has_asthma:
        warnings.append("Cold climate warning: Srinagar's cold temperatures might trigger asthma. Ensure inhalers are handy.")
        alternative_indoors.append("Shikara ride with enclosed charcoal heaters")
    if dest_name.lower() == "goa" and has_elderly:
        warnings.append("Heat warning: High humidity in Goa. Keep elderly travelers well hydrated and avoid direct sun during peak hours.")
        alternative_indoors.append("Indoor beachside lounges & local churches")
    if dest_name.lower() == "jaipur" and has_knee_pain:
        warnings.append("Mobility warning: Historic forts in Jaipur have steep stone steps and gravel paths.")
        alternative_indoors.append("Palace museum guided indoor walking tours")
        
    weather_safety = WeatherSafetyDetail(
        general_condition=dest["weather_profile"]["general_condition"],
        health_warnings=warnings if warnings else ["No major medical risks identified for the current traveler profiles."],
        alternative_indoor_activities=alternative_indoors
    )
    
    # 6. Expectation vs Reality Match
    exp_lower = request.expectations.lower()
    score = 85
    matching = ["Vibe matches user preferences"]
    deviating = []
    
    if "peaceful" in exp_lower or "less crowd" in exp_lower:
        if dest_name.lower() in ["goa", "jaipur"]:
            score -= 15
            deviating.append("Highly touristy areas might get crowded during weekends.")
            matching.append("Early morning visits can bypass crowds.")
        else:
            matching.append("Quiet spots like gardens or lakes are easily accessible.")
            
    if "sunset" in exp_lower:
        matching.append("Excellent scenic sunset points are part of the main itinerary.")
        
    expectation_reality = MatchScoreDetail(
        score=score,
        matching_aspects=matching,
        deviating_aspects=deviating,
        reality_check_summary=f"The destination matches the group's vibes well. {dest['description']}"
    )
    
    # 7. Hotels Selection based on preferences (accommodation preference and food taste)
    pref_tier = request.travelers[0].accommodation_preference.lower()
    pref_food = request.travelers[0].food_preference.lower()
    limit_count = max(3, min(10, request.hotel_count))
    all_dest_hotels = places_service.get_live_hotels(dest_name, pref_tier, limit_count)
    
    # Sort hotels: matches food style (veg/vegan), matches lodging tier, then rating
    def hotel_sort_key(hotel):
        tier_score = 0 if hotel["tier"].lower() == pref_tier else 1
        food_score = 0
        if pref_food in ["veg", "vegan"]:
            has_veg = any("vegetarian" in a.lower() or "veg" in a.lower() for a in hotel.get("amenities", [])) or \
                      any("veg" in r.lower() or "pure vegetarian" in r.lower() for r in hotel.get("reviews", []))
            food_score = 0 if has_veg else 1
        return (food_score, tier_score, -hotel["rating"])
        
    sorted_hotels = sorted(all_dest_hotels, key=hotel_sort_key)
    selected_hotels = sorted_hotels[:limit_count]
    
    hotels_recommendations = [
        HotelRecommendation(
            name=h["name"],
            price_per_night=h["price_per_night"],
            rating=h["rating"],
            amenities=h.get("amenities", []),
            reviews=h.get("reviews", []),
            specialty_keyword=h.get("specialty_keyword", "Value for Money")
        ) for h in selected_hotels
    ]
    
    # 8. Itineraries (Group, Solo, Reunion with Conflict Resolver)
    group_itinerary = []
    solo_itineraries = {}
    reunion_schedule = []
    
    # Query live attractions via Google Places (with mock fallback built-in)
    live_attractions = places_service.get_live_attractions(dest_name, limit=15)
    
    # Let's populate days
    for day_idx in range(1, num_days + 1):
        # Group Day Activity
        group_attraction = live_attractions[day_idx % len(live_attractions)]
        group_act = ItineraryActivity(
            time="Morning (10:00 AM - 1:00 PM)",
            activity_name=group_attraction["name"],
            description=group_attraction["description"],
            estimated_cost=group_attraction["cost"],
            fatigue_level=group_attraction["fatigue_index"],
            assigned_to=["All"]
        )
        group_itinerary.append(ItineraryDay(day=day_idx, activities=[group_act]))
        
        # Solo Itinerary Activities (If preferences differ - Conflict Resolver Agent)
        for t in request.travelers:
            if t.name not in solo_itineraries:
                solo_itineraries[t.name] = []
            
            # Active/younger travelers vs senior/relaxed travelers
            is_active = t.age < 35 or any(v in t.vibe_preference.lower() for v in ["nightlife", "adventure"])
            
            # Select attraction based on activity profile
            solo_attraction = None
            for attr in live_attractions:
                fatigue = attr["fatigue_index"]
                if is_active and fatigue >= 3:
                    solo_attraction = attr
                    break
                elif not is_active and fatigue <= 2:
                    solo_attraction = attr
                    break
                    
            if not solo_attraction:
                solo_attraction = live_attractions[1 % len(live_attractions)]
                
            solo_act = ItineraryActivity(
                time="Afternoon (2:30 PM - 5:30 PM)",
                activity_name=solo_attraction["name"],
                description=f"Conflict Resolver Agent: {t.name} scheduled for this {t.vibe_preference}-matching activity. {solo_attraction['description']}",
                estimated_cost=solo_attraction["cost"],
                fatigue_level=solo_attraction["fatigue_index"],
                assigned_to=[t.name]
            )
            
            # Check if this day exists in their solo schedule
            day_found = False
            for s_day in solo_itineraries[t.name]:
                if s_day.day == day_idx:
                    s_day.activities.append(solo_act)
                    day_found = True
                    break
            if not day_found:
                solo_itineraries[t.name].append(ItineraryDay(day=day_idx, activities=[solo_act]))
        
        # Reunion evening activity (Dinner & Gathering)
        reunion_dining = "Local Dinner & Gathering"
        if len(hotels_recommendations) > 0:
            reunion_dining = f"Dinner at {hotels_recommendations[day_idx % len(hotels_recommendations)].name}"
            
        reunion_act = ItineraryActivity(
            time="Evening (7:00 PM - 9:30 PM)",
            activity_name=reunion_dining,
            description="Conflict Resolver Agent: Group gathers back together to share experiences and enjoy meals matching everyone's food tastes.",
            estimated_cost=300,
            fatigue_level=1,
            assigned_to=["All"]
        )
        reunion_schedule.append(ItineraryDay(day=day_idx, activities=[reunion_act]))
        
    # 9. Explainable AI Reasons ("Why this recommendation?")
    xai_reasons = [
        f"Selected {dest['name']} as it has the optimal overlap of vibes: {', '.join(dest['vibes'][:3])}.",
        f"Suitable for senior citizens & health concerns (weather is {weather_cond.lower()}).",
        f"Within your target budget (estimated daily per person spend fits lodging tier).",
        f"Excellent dining options nearby matching all dietary preference lists ({pref_food} options)."
    ]
    
    # 10. Smart Budget Expansions (Click to see changes upsell)
    smart_expansions = [
        "Do you know? If you are willing to spend an extra 2000 INR, you could visit two more places Click here to see the changes",
        "Do you know? If you are willing to spend an extra 5000 INR, you can upgrade your stay to a premium luxury hotel Click here to see the changes"
    ]
    
    return RecommendationResponse(
        destination_name=dest["name"],
        description=dest["description"],
        group_compatibility_score=comp_score,
        group_itinerary=group_itinerary,
        solo_itineraries=solo_itineraries,
        reunion_schedule=reunion_schedule,
        conflict_resolution_summary="Successfully split the afternoon tracks to accommodate individual vibes, reuniting the group each evening for dinners.",
        budget_analysis=budget_analysis,
        weather_health_safety=weather_safety,
        expectation_reality_match=expectation_reality,
        explainable_ai_reasons=xai_reasons,
        smart_budget_expansions=smart_expansions,
        hotels=hotels_recommendations
    )

def run_travel_recommendation_crew(request: TravelGroupRequest) -> RecommendationResponse:
    """
    Kicks off the CrewAI multi-agent travel orchestration.
    Falls back gracefully to the mock recommendation engine if the LLM is configured as 'mock'
    or if API keys are missing.
    """
    llm = travel_agents.get_llm()
    
    if llm is None or not CREWAI_AVAILABLE or Crew is None or Process is None:
        # Fall back to simulation
        return generate_mock_recommendation(request)
        
    try:
        # Create the CrewAI agents
        pref_agent = travel_agents.create_preference_agent(llm)
        budget_agent = travel_agents.create_budget_agent(llm)
        weather_agent = travel_agents.create_weather_agent(llm)
        accomm_agent = travel_agents.create_accommodation_agent(llm)
        itinerary_agent = travel_agents.create_itinerary_agent(llm)
        conflict_agent = travel_agents.create_conflict_agent(llm)
        expectation_agent = travel_agents.create_expectation_agent(llm)
        
        # Package data
        travelers_str = ", ".join([
            f"{t.name} (Age: {t.age}, Vibe: {t.vibe_preference}, Medical: {t.medical_conditions})"
            for t in request.travelers
        ])
        
        # Choose destination
        dest_name = request.destination_preference or "Goa"
        dest_dict = mock_db.get_destination(dest_name) or mock_db.get_destination("Goa")
        if not dest_dict:
            dest_dict = mock_db.DESTINATIONS["goa"]
        dest: Dict[str, Any] = dest_dict
        
        # Query live Google Places hotels and attractions (with automatic fallback to mock_db)
        live_hotels = places_service.get_live_hotels(dest_name, request.travelers[0].accommodation_preference.lower(), request.hotel_count)
        live_attractions = places_service.get_live_attractions(dest_name, limit=15)
        
        # Create the CrewAI tasks
        task_pref = travel_tasks.create_preference_task(pref_agent, travelers_str)
        task_budget = travel_tasks.create_budget_task(budget_agent, request.total_budget, request.num_days)
        task_weather = travel_tasks.create_weather_health_task(
            weather_agent, 
            str(dest["weather_profile"]), 
            ", ".join([f"{t.name}: {t.medical_conditions}" for t in request.travelers])
        )
        task_accomm = travel_tasks.create_accommodation_task(
            accomm_agent, 
            str(live_hotels), 
            request.travelers[0].accommodation_preference
        )
        task_itinerary = travel_tasks.create_itinerary_task(
            itinerary_agent, 
            request.num_days, 
            str(live_attractions)
        )
        task_conflict = travel_tasks.create_conflict_resolution_task(conflict_agent)
        task_expectation = travel_tasks.create_expectation_match_task(
            expectation_agent, 
            request.expectations, 
            str([h["reviews"] for h in live_hotels])
        )
        
        # Assemble the Crew
        # We set up a sequential execution flow for our agents to collaborate
        travel_crew = Crew(
            agents=[
                pref_agent, 
                budget_agent, 
                weather_agent, 
                accomm_agent, 
                itinerary_agent, 
                conflict_agent, 
                expectation_agent
            ],
            tasks=[
                task_pref, 
                task_budget, 
                task_weather, 
                task_accomm, 
                task_itinerary, 
                task_conflict, 
                task_expectation
            ],
            process=Process.sequential,
            verbose=True
        )
        
        # Run the crew
        crew_output = travel_crew.kickoff()
        
        # In a full production implementation, we parse the crew output (usually structured as JSON)
        # and map it into our RecommendationResponse schema.
        # For this hackathon backend skeleton, we parse it if it is JSON, or we use our mock generator 
        # as a structured response wrapper around the crew's textual findings.
        parsed_json = parse_json_safely(str(crew_output))
        
        if parsed_json and "destination_name" in parsed_json:
            # If the LLM successfully outputted exact JSON matching our structure, return it
            try:
                return RecommendationResponse(**parsed_json)
            except Exception:
                pass
                
        # Default fallback to guarantee structured schema validation
        return generate_mock_recommendation(request)
    except Exception as e:
        print(f"CrewAI execution failed: {e}. Falling back to high-quality local generator.")
        return generate_mock_recommendation(request)
