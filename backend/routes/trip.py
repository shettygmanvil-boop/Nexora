from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from backend.models.trip import (
    Traveler,
    GroupTripRequest,
    DestinationDetail,
    RecommendationResponse
)
from backend.database.destinations import (
    get_all_destinations,
    get_destination_by_name,
    get_destinations_by_vibe
)

router = APIRouter(prefix="", tags=["Trip Planning & Destinations"])

@router.get("/destinations", response_model=List[DestinationDetail])
def get_destinations(vibe: Optional[str] = Query(None, description="Filter destinations by vibe (e.g. 'nightlife', 'beaches', 'mountains')")):
    """
    Get all destinations or filter them by a specific vibe.
    
    Returns a structured JSON list of matching destinations.
    """
    try:
        if vibe:
            results = get_destinations_by_vibe(vibe)
            return [DestinationDetail(**dest) for dest in results]
        else:
            results = get_all_destinations()
            return [DestinationDetail(**dest) for dest in results]
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal database query error: {str(e)}")


@router.get("/destinations/{name}", response_model=DestinationDetail)
def get_destination_detail(name: str):
    """
    Get full details of a specific destination by its name (case-insensitive).
    """
    try:
        dest = get_destination_by_name(name)
        return DestinationDetail(**dest)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving destination details: {str(e)}")


@router.post("/validate-trip", response_model=RecommendationResponse)
def validate_trip(request: GroupTripRequest):
    """
    Validates a group trip request parameters, checks compatibility with the database 
    and returns a structured simulation response.
    
    Includes detailed budget suitability analysis, compatibility calculations,
    suggested activities, and critical health/safety warnings based on traveler parameters.
    """
    try:
        # 1. Determine the destination to recommend based on preference or vibe
        recommended_dest = None
        if request.destination_preference:
            try:
                recommended_dest = get_destination_by_name(request.destination_preference)
            except ValueError:
                # If preferred destination is not found, raise a bad request error
                raise HTTPException(
                    status_code=400, 
                    detail=f"Preferred destination '{request.destination_preference}' is currently not supported. Supported destinations: Goa, Bangalore, Srinagar, Jaipur."
                )
        else:
            # Try to match by vibe
            matches = get_destinations_by_vibe(request.preferred_vibe)
            if matches:
                # Pick the highest matching score destination or first match
                recommended_dest = matches[0]
            else:
                # Default to Goa if no vibe matches
                try:
                    recommended_dest = get_destination_by_name("Goa")
                except ValueError:
                    # Fallback to first available destination in database
                    all_dests = get_all_destinations()
                    if all_dests:
                        recommended_dest = all_dests[0]
                    else:
                        raise HTTPException(status_code=500, detail="No destinations available in database.")

        dest_name = recommended_dest["name"]
        
        # 2. Compute a dynamic compatibility score (0 to 100)
        # Base compatibility score
        compatibility = 70.0
        
        # Add points if destination matches requested vibe
        if request.preferred_vibe.lower() in recommended_dest.get("vibes", []):
            compatibility += 15.0
            
        # Check budget friendliness alignment
        avg_budget_per_day = request.budget / (request.days * len(request.travelers))
        if avg_budget_per_day < 3000 and recommended_dest.get("budget_friendliness", 0) >= 7:
            compatibility += 10.0
        elif avg_budget_per_day >= 8000 and recommended_dest.get("luxury_score", 0) >= 8:
            compatibility += 10.0
        else:
            compatibility += 5.0
            
        # Check senior citizen friendliness
        has_senior = any(t.age >= 60 for t in request.travelers)
        if has_senior:
            if recommended_dest.get("senior_citizen_friendliness", 0) >= 7:
                compatibility += 5.0
            else:
                compatibility -= 10.0  # deduction for lack of senior features
                
        # Limit between 0 and 100
        compatibility = max(0.0, min(100.0, compatibility))
        
        # 3. Generate dynamic reasons list
        reasons = [
            f"The destination '{dest_name}' aligns well with your group vibe preference of '{request.preferred_vibe}'.",
            f"Its adventure score is {recommended_dest.get('adventure_score')}/10, matching your active group profile." if not has_senior else f"Its peacefulness score is {recommended_dest.get('peacefulness_score')}/10, suitable for relaxed family trip.",
            f"Veg food availability in {dest_name} is rated '{recommended_dest.get('veg_food_availability')}', which is perfect for vegetarians in the group."
        ]
        
        # 4. Generate budget summary
        budget_level = "economy"
        if avg_budget_per_day >= 8000:
            budget_level = "premium/luxury"
        elif avg_budget_per_day >= 4000:
            budget_level = "standard"
            
        budget_summary = (
            f"Total combined budget is ₹{request.budget:,.2f} for {request.days} days ({len(request.travelers)} traveler(s)). "
            f"This averages to ₹{avg_budget_per_day:,.2f} per traveler per day, which comfortably supports a {budget_level} stay "
            f"in {dest_name}."
        )
        
        # 5. Generate traveler-specific medical and weather warnings
        warnings = []
        
        # Weather warnings
        weather_type = recommended_dest.get("weather_type", "")
        if weather_type == "Warm & Humid" or weather_type == "Hot & Dry":
            warnings.append(f"Climate warning: {dest_name} is currently experiencing {weather_type} conditions. Make sure all travelers carry hydration packs.")
        elif weather_type == "Cold":
            warnings.append(f"Climate warning: {dest_name} is currently Cold. Make sure all travelers pack high-quality thermal wear.")
            
        # Medical warnings based on destination risk notes and traveler conditions
        medical_notes = recommended_dest.get("medical_risk_notes", "")
        for traveler in request.travelers:
            if traveler.medical_conditions:
                for condition in traveler.medical_conditions:
                    warnings.append(
                        f"Medical warning for {traveler.name} ({condition}): {medical_notes}"
                    )
        
        # Default safety warning if empty
        if not warnings:
            warnings.append("No specific environmental or medical warning triggers detected.")
            
        return RecommendationResponse(
            recommended_destination=dest_name,
            compatibility_score=compatibility,
            reasons=reasons,
            suggested_activities=recommended_dest.get("top_activities", []),
            budget_summary=budget_summary,
            warnings=warnings
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trip validation simulation failure: {str(e)}")
