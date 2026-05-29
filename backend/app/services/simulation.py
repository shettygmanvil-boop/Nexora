from typing import List, Dict, Any
from app.schemas.travel import (
    TravelerProfile, 
    SimulationResponse, 
    BudgetAllocation
)
from app.database import mock_db
from app.utils.helpers import calculate_compatibility

def simulate_budget_adjustment(
    destination_name: str,
    target_budget: float,
    num_days: int,
    travelers: List[TravelerProfile]
) -> SimulationResponse:
    """
    Simulates changes to lodging, activities, compatibility, and upgrades
    when the user adjusts the budget slider.
    """
    dest_dict = mock_db.DESTINATIONS.get(destination_name.lower())
    if not dest_dict:
        dest_dict = mock_db.DESTINATIONS["goa"]
        destination_name = "Goa"
    dest: Dict[str, Any] = dest_dict
        
    # Calculate new allocation
    accom_cost = target_budget * 0.45
    activities_cost = target_budget * 0.35
    buffer_amt = target_budget * 0.10
    remaining = target_budget - (accom_cost + activities_cost + buffer_amt)
    
    explanation = (
        f"Recalculated allocations for {destination_name} based on the adjusted budget of {target_budget} INR. "
        "Lodging scale, sightseeing coverage, and contingency buffers have been adjusted accordingly."
    )
    
    updated_budget = BudgetAllocation(
        accommodation_cost=round(accom_cost, 2),
        activities_cost=round(activities_cost, 2),
        buffer_amount=round(buffer_amt, 2),
        remaining_balance=round(remaining, 2),
        explanation=explanation
    )
    
    # Analyze upgrades/downgrades and itinerary changes
    suggested_upgrades = []
    itinerary_changes = []
    
    # Accommodation options in destination
    hotels = sorted(dest["hotels"], key=lambda x: x["price_per_night"])
    # Standard cost estimate for hotels based on target_budget / num_days
    nightly_allowance = accom_cost / max(1, num_days)
    
    selected_hotel = hotels[0]
    for hotel in hotels:
        if hotel["price_per_night"] <= nightly_allowance:
            selected_hotel = hotel
            
    itinerary_changes.append(f"Recommended accommodation: {selected_hotel['name']} ({selected_hotel['tier'].capitalize()} tier) at {selected_hotel['price_per_night']} INR/night.")
    
    # Check if a higher tier hotel is available but locked
    for hotel in hotels:
        if hotel["price_per_night"] > nightly_allowance:
            diff = (hotel["price_per_night"] * num_days) - accom_cost
            suggested_upgrades.append(
                f"Upgrade to '{hotel['name']}' ({hotel['tier'].capitalize()} tier) by adding approx {round(diff, 0)} INR to lodging budget."
            )
            
    # Attraction simulation
    unlocked_attractions = []
    for attr in dest["attractions"]:
        if attr["cost"] <= activities_cost:
            unlocked_attractions.append(attr["name"])
            
    itinerary_changes.append(f"Sightseeing package unlocks: {', '.join(unlocked_attractions[:3])}.")
    
    # Suggest premium activities if budget permits
    expensive_attractions = [a for a in dest["attractions"] if a["cost"] > 1000]
    for exp_a in expensive_attractions:
        if exp_a["cost"] > activities_cost:
            diff = exp_a["cost"] - activities_cost
            suggested_upgrades.append(f"Add premium experience '{exp_a['name']}' (Cost: {exp_a['cost']} INR). Requires {round(diff, 0)} INR extra.")
            
    # Base compatibility update
    base_comp = calculate_compatibility(travelers, dest["vibes"])
    # Increase compatibility slightly if budget allows more personalized solo activities
    if target_budget > 30000:
        base_comp = min(100.0, base_comp + 5.0)
    elif target_budget < 10000:
        base_comp = max(40.0, base_comp - 10.0)
        
    return SimulationResponse(
        updated_budget_allocation=updated_budget,
        suggested_upgrades=suggested_upgrades if suggested_upgrades else ["All available upgrades unlocked!"],
        compatibility_score=base_comp,
        itinerary_changes=itinerary_changes
    )
