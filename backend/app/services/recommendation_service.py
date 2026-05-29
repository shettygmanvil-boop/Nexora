"""
Recommendation Service for Maproom

Implements fully deterministic, offline, and rule-based travel destination recommendation logic.
Calculates weighted compatibility scores across 8 factors:
1. Mood match (15%)
2. Travel purpose match (15%)
3. Budget suitability (15%)
4. Vibe match (15%)
5. Age suitability (10%)
6. Medical suitability (10%)
7. Activity level compatibility (10%)
8. Food preference compatibility (10%)
"""

from typing import List, Dict, Any, Tuple
from app.models.trip import GroupTripRequest, RecommendationDetails, ExpectationMatchResponse, Traveler
from app.database.destinations import get_all_destinations

# Factor weights adding up to 1.0 (100%)
WEIGHTS = {
    "mood_match": 0.15,
    "travel_purpose_match": 0.15,
    "budget_suitability": 0.15,
    "vibe_match": 0.15,
    "age_suitability": 0.10,
    "medical_suitability": 0.10,
    "activity_level_compatibility": 0.10,
    "food_preference_compatibility": 0.10,
}


def calculate_mood_match(travelers: List[Traveler], destination: Dict[str, Any]) -> float:
    """Matches traveler mood (relaxed/chill/adventurous/excited) against destination stats."""
    if not travelers:
        return 100.0
    
    scores = []
    peace = destination.get("peacefulness_score", 5)
    adv = destination.get("adventure_score", 5)
    night = destination.get("nightlife_score", 5)
    
    for t in travelers:
        mood = t.mood.strip().lower()
        if mood in ("relaxed", "chill"):
            scores.append(peace * 10.0)
        elif mood == "adventurous":
            scores.append(adv * 10.0)
        elif mood == "excited":
            scores.append(max(night, adv) * 10.0)
        else:
            # Fallback to general average
            scores.append(((peace + adv + night) / 3.0) * 10.0)
            
    return round(sum(scores) / len(travelers), 2)


def calculate_travel_purpose_match(travelers: List[Traveler], destination: Dict[str, Any]) -> float:
    """Calculates compatibility of traveler purpose (adventure, relaxation, etc.) with destination."""
    if not travelers:
        return 100.0
        
    scores = []
    peace = destination.get("peacefulness_score", 5)
    adv = destination.get("adventure_score", 5)
    lux = destination.get("luxury_score", 5)
    fam = destination.get("family_friendliness", 5)
    vibes = [v.lower() for v in destination.get("vibes", [])]
    dest_name_lower = destination.get("name", "").strip().lower()
    
    for t in travelers:
        purpose = t.travel_purpose.strip().lower()
        if purpose == "adventure":
            scores.append(adv * 10.0)
        elif purpose in ("relaxation", "digital detox"):
            scores.append(peace * 10.0)
        elif purpose == "spirituality":
            if "spirituality" in vibes or "temples" in vibes:
                scores.append(100.0)
            elif peace >= 7:
                scores.append(85.0)
            else:
                scores.append(60.0)
        elif purpose == "nature exploration":
            if any(v in vibes for v in ("nature", "scenic", "coastal", "gardens")):
                scores.append(100.0)
            elif peace >= 7:
                scores.append(85.0)
            else:
                scores.append(60.0)
        elif purpose == "workcation":
            if "workcation" in vibes:
                scores.append(100.0)
            elif destination.get("weather_type", "") == "Pleasant":
                scores.append(80.0)
            else:
                scores.append(60.0)
        elif purpose == "luxury":
            scores.append(lux * 10.0)
        elif purpose == "photography":
            if any(v in vibes for v in ("photography", "scenic", "heritage")):
                scores.append(100.0)
            else:
                scores.append(70.0)
        elif purpose in ("leisure", "family bonding"):
            scores.append(fam * 10.0)
        elif purpose == "business":
            if dest_name_lower == "bangalore":
                scores.append(100.0)
            else:
                scores.append(70.0)
        else:
            scores.append(fam * 10.0)
            
    return round(sum(scores) / len(travelers), 2)


def calculate_age_suitability(travelers: List[Traveler], destination: Dict[str, Any]) -> float:
    """Scores suitability based on age demographics, factoring crowd level and nightlife noise."""
    if not travelers:
        return 100.0
        
    scores = []
    senior_friendliness = destination.get("senior_citizen_friendliness", 5)
    family_friendliness = destination.get("family_friendliness", 5)
    crowd_level = destination.get("crowd_level", "Medium").strip().lower()
    night = destination.get("nightlife_score", 5)
    
    for t in travelers:
        age = t.age
        if age >= 60:
            base = senior_friendliness * 10.0
            if crowd_level == "high":
                base -= 10.0
            if night >= 8:
                base -= 15.0
            scores.append(max(20.0, min(100.0, base)))
        elif age <= 12:
            base = family_friendliness * 10.0
            if crowd_level == "high":
                base -= 10.0
            scores.append(max(30.0, min(100.0, base)))
        else:
            scores.append(100.0)
            
    return round(sum(scores) / len(travelers), 2)


def calculate_food_preference_compatibility(travelers: List[Traveler], destination: Dict[str, Any]) -> float:
    """Scores food preference alignment based on veg food availability."""
    if not travelers:
        return 100.0
        
    scores = []
    veg_availability = destination.get("veg_food_availability", "Medium").strip().lower()
    
    for t in travelers:
        food = t.food_preference.strip().lower()
        if food in ("veg", "vegan"):
            if veg_availability == "high":
                scores.append(100.0)
            elif veg_availability == "medium":
                scores.append(80.0)
            else:
                scores.append(50.0)
        else:
            scores.append(95.0)
            
    return round(sum(scores) / len(travelers), 2)


def calculate_medical_suitability(travelers: List[Traveler], destination: Dict[str, Any]) -> float:
    """Flags medical concerns against environment/climate profile to compute safety-suitability."""
    if not travelers:
        return 100.0
        
    scores = []
    weather = destination.get("weather_type", "").strip().lower()
    adv = destination.get("adventure_score", 5)
    dest_name_lower = destination.get("name", "").strip().lower()
    
    for t in travelers:
        base = 100.0
        conditions = [c.strip().lower() for c in t.medical_conditions]
        
        for condition in conditions:
            if "asthma" in condition or "respiratory" in condition:
                if weather == "cold":
                    base -= 40.0
                elif dest_name_lower == "bangalore":
                    base -= 20.0
                else:
                    base -= 10.0
            if "hypertension" in condition or "heart" in condition:
                if weather == "hot & dry":
                    base -= 30.0
                elif weather == "warm & humid":
                    base -= 25.0
                elif weather == "cold":
                    base -= 15.0
            if any(k in condition for k in ("knee", "mobility", "arthritis", "joint")):
                if adv >= 7:
                    base -= 30.0
                else:
                    base -= 10.0
        scores.append(max(20.0, base))
        
    return round(sum(scores) / len(travelers), 2)


def calculate_budget_suitability(budget: float, days: int, travelers: List[Traveler], destination: Dict[str, Any]) -> float:
    """Matches group budget per person per day against hotel cost expectations."""
    if not travelers or days <= 0:
        return 50.0
        
    avg_budget_per_day = budget / (days * len(travelers))
    budget_friendliness = destination.get("budget_friendliness", 5)
    luxury = destination.get("luxury_score", 5)
    
    scores = []
    for t in travelers:
        pref = t.budget_preference.strip().lower()
        if avg_budget_per_day < 3000:
            base = budget_friendliness * 10.0
            if pref == "luxury":
                base -= 20.0
            scores.append(max(20.0, min(100.0, base)))
        elif avg_budget_per_day <= 7000:
            if pref == "budget":
                scores.append(95.0)
            elif pref == "luxury":
                scores.append(85.0)
            else:
                scores.append(90.0)
        else:
            base = luxury * 10.0
            if pref == "luxury":
                base += 10.0
            elif pref == "budget":
                base -= 10.0
            scores.append(max(50.0, min(100.0, base)))
            
    return round(sum(scores) / len(travelers), 2)


def calculate_vibe_match(preferred_vibe: str, destination: Dict[str, Any]) -> float:
    """Scores vibe matching from 40 to 100 based on exact/fallback tag checks."""
    vibe_query = preferred_vibe.strip().lower()
    vibes = [v.lower() for v in destination.get("vibes", [])]
    
    if vibe_query in vibes:
        return 100.0
        
    # Categories alignment mapping
    if vibe_query == "nightlife" and destination.get("nightlife_score", 0) >= 7:
        return 85.0
    elif vibe_query in ("peaceful", "peacefulness", "relaxation") and destination.get("peacefulness_score", 0) >= 7:
        return 85.0
    elif vibe_query == "adventure" and destination.get("adventure_score", 0) >= 7:
        return 85.0
    elif vibe_query == "luxury" and destination.get("luxury_score", 0) >= 7:
        return 85.0
    elif vibe_query in ("heritage", "culture", "history") and (destination.get("name", "").strip().lower() == "jaipur" or "heritage" in vibes):
        return 85.0
    elif vibe_query == "beaches" and "coastal" in vibes:
        return 85.0
    elif vibe_query == "mountains" and "cold" in vibes:
        return 85.0
        
    return 40.0


def calculate_activity_level_compatibility(travelers: List[Traveler], destination: Dict[str, Any]) -> float:
    """Checks how well travelers' activity preferences align with destination attributes."""
    if not travelers:
        return 100.0
        
    adv = destination.get("adventure_score", 5)
    peace = destination.get("peacefulness_score", 5)
    senior = destination.get("senior_citizen_friendliness", 5)
    
    scores = []
    for t in travelers:
        level = t.activity_level.strip().lower()
        if level == "high":
            scores.append(adv * 10.0)
        elif level == "low":
            scores.append(((peace + senior) / 2.0) * 10.0)
        else:
            scores.append(90.0)
            
    return round(sum(scores) / len(travelers), 2)


def calculate_expectation_match(
    preferred_vibe: str,
    priorities: List[str],
    expectations: str,
    destination: Dict[str, Any]
) -> Tuple[float, str]:
    """Evaluates verbal requests and group priorities against the destination."""
    score = 60.0
    matching_aspects = []
    deviating_aspects = []
    
    dest_name = destination.get("name", "")
    dest_vibes = [v.lower() for v in destination.get("vibes", [])]
    weather = destination.get("weather_type", "").strip().lower()
    
    # 1. Match preferred vibe
    vibe_query = preferred_vibe.strip().lower()
    if vibe_query in dest_vibes:
        score += 15.0
        matching_aspects.append(f"Vibe preference '{preferred_vibe}' matches {dest_name}'s atmosphere.")
    else:
        deviating_aspects.append(f"Vibe preference '{preferred_vibe}' does not match {dest_name}'s vibes.")
        
    # 2. Match priorities
    priority_score = 0.0
    for prio in priorities:
        p_lower = prio.strip().lower()
        matched = False
        if p_lower in ("party", "nightlife") and destination.get("nightlife_score", 0) >= 7:
            matched = True
        elif p_lower in ("relaxation", "peacefulness") and destination.get("peacefulness_score", 0) >= 7:
            matched = True
        elif p_lower in ("adventure", "sports") and destination.get("adventure_score", 0) >= 7:
            matched = True
        elif p_lower in ("food", "dining", "cafe") and (destination.get("veg_food_availability", "Medium") == "High" or dest_name.lower() in ("bangalore", "goa")):
            matched = True
        elif p_lower in ("sightseeing", "heritage", "culture") and (destination.get("family_friendliness", 0) >= 7 or "heritage" in dest_vibes):
            matched = True
            
        if matched:
            priority_score += 5.0
            matching_aspects.append(f"Priority '{prio}' aligns well with {dest_name}'s characteristics.")
        else:
            deviating_aspects.append(f"Priority '{prio}' is not a primary highlight of {dest_name}.")
            
    score += min(20.0, priority_score)
    
    # 3. Keyword Match on expectations
    exp_lower = expectations.lower() if expectations else ""
    keyword_score = 0.0
    
    keywords_positive = {
        ("peaceful", "quiet", "calm", "relax", "lake", "sunset"): (destination.get("peacefulness_score", 0) >= 7, "peacefulness and quiet vibe"),
        ("party", "nightlife", "dance", "club", "beer", "alcohol", "pub"): (destination.get("nightlife_score", 0) >= 7, "nightlife and party options"),
        ("trek", "adventure", "scuba", "water sports", "climb", "hike"): (destination.get("adventure_score", 0) >= 7, "outdoor adventure activities"),
        ("history", "royal", "palace", "fort", "heritage", "temple", "culture"): ("heritage" in dest_vibes or dest_name.lower() == "jaipur", "rich historical heritage"),
        ("cafe", "coffee", "tech", "garden", "urban"): (dest_name.lower() == "bangalore", "vibrant cafe and garden culture"),
        ("cold", "snow", "mountain"): (weather == "cold", "mountain landscapes and cold climate"),
        ("beach", "sea", "ocean", "sand", "sun"): ("beaches" in dest_vibes or "coastal" in dest_vibes, "beach and coastal beauty")
    }
    
    matched_positives = []
    matched_negatives = []
    
    if exp_lower:
        for kw_tuple, (condition_met, desc) in keywords_positive.items():
            if any(kw in exp_lower for kw in kw_tuple):
                if condition_met:
                    keyword_score += 10.0
                    matched_positives.append(desc)
                else:
                    score -= 15.0
                    matched_negatives.append(desc)
                    
        score += min(20.0, keyword_score)
        
    score = max(0.0, min(100.0, score))
    
    # Narrative Building
    if matched_positives:
        summary_pos = f"Excellent match for your expectations regarding {', '.join(matched_positives)}."
    else:
        summary_pos = f"{dest_name} offers a general travel experience."
        
    if matched_negatives:
        summary_neg = f" Note that it may not fully meet expectations for {', '.join(matched_negatives)}."
    else:
        summary_neg = ""
        
    summary = f"{summary_pos}{summary_neg} overall, matching aspects include: {'; '.join(matching_aspects[:2])}."
    if deviating_aspects:
        summary += f" Minor mismatches: {'; '.join(deviating_aspects[:2])}."
        
    return round(score, 2), summary


def generate_smart_warnings(request: GroupTripRequest, destination: Dict[str, Any]) -> List[str]:
    """Evaluates safety profiles and group details to trigger logical warnings."""
    warnings = []
    dest_name = destination.get("name", "")
    weather = destination.get("weather_type", "").strip().lower()
    crowd = destination.get("crowd_level", "Medium").strip().lower()
    night = destination.get("nightlife_score", 5)
    adv = destination.get("adventure_score", 5)
    
    num_travelers = len(request.travelers)
    avg_budget_per_day = request.budget / (request.days * num_travelers) if request.days > 0 and num_travelers > 0 else 0
    
    for t in request.travelers:
        conditions_lower = [c.lower().strip() for c in t.medical_conditions]
        
        # 1. Asthma + Cold weather or pollution
        if "asthma" in conditions_lower or "respiratory" in conditions_lower:
            if weather == "cold":
                warnings.append(
                    f"Asthma Alert: {t.name} has asthma, which can be triggered by Srinagar's cold climate. "
                    f"Ensure warm clothing and carry rescue inhalers."
                )
            if dest_name.lower() == "bangalore":
                warnings.append(
                    f"Pollution Alert: {t.name} has asthma. Bangalore has moderate pollution levels; check AQI status."
                )
                
        # 2. Low Budget + Luxury Mismatch
        if t.budget_preference.strip().lower() == "luxury" and avg_budget_per_day < 3000:
            warnings.append(
                f"Budget Mismatch: {t.name} prefers luxury services, but the average daily budget of "
                f"₹{avg_budget_per_day:.0f} per person is more suited for economy/standard accommodation."
            )
            
        # 3. Senior Citizen + Crowded Nightlife
        if t.age >= 60:
            if crowd == "high" and night >= 8:
                warnings.append(
                    f"Crowd & Noise Warning: {t.name} is a senior citizen. {dest_name} has high crowd levels "
                    f"and an active nightlife, which may not be comfortable for elderly travelers."
                )
                
        # 4. Knee pain + high fatigue/adventure
        if any(k in c for c in conditions_lower for k in ("knee", "mobility", "arthritis", "joint")):
            if adv >= 7:
                warnings.append(
                    f"Mobility Alert: {t.name} has joint/mobility issues. {dest_name} features high-fatigue "
                    f"activities (e.g. trekking/adventure) which may strain joints."
                )
                
        # 5. Hypertension + Extreme Heat
        if "hypertension" in conditions_lower or "heart" in conditions_lower:
            if weather in ("hot & dry", "warm & humid"):
                warnings.append(
                    f"Medical Alert: {t.name} has hypertension. {dest_name} is experiencing hot/humid conditions "
                    f"({destination.get('weather_type')}), increasing dehydration and cardiovascular strain."
                )
                
    if not warnings:
        warnings.append("No specific environmental or medical warning triggers detected.")
        
    return warnings


def generate_recommendation_reasons(
    preferred_vibe: str,
    priorities: List[str],
    destination: Dict[str, Any],
    factor_scores: Dict[str, float]
) -> List[str]:
    """Generates user-friendly reasons explaining the destination match."""
    reasons = []
    dest_name = destination.get("name", "")
    
    # 1. Vibe check
    if factor_scores["vibe_match"] >= 80:
        reasons.append(f"Excellent match with your group's preferred vibe of '{preferred_vibe}'.")
        
    # 2. Nightlife lover condition
    if destination.get("nightlife_score", 0) >= 8 and "nightlife" in preferred_vibe.lower():
        reasons.append(f"Premier nightlife destination with a score of {destination.get('nightlife_score')}/10.")
        
    # 3. Food compatibility check
    if factor_scores["food_preference_compatibility"] >= 80:
        veg_status = destination.get("veg_food_availability", "Medium")
        reasons.append(f"Good veg food options available ({veg_status} availability).")
        
    # 4. Activity level compatibility check
    if factor_scores["activity_level_compatibility"] >= 80:
        reasons.append(f"Strong group activity options matching everyone's physical levels.")
        
    # 5. Budget suitability check
    if factor_scores["budget_suitability"] >= 85:
        reasons.append("Highly suited for your group budget allocation.")
        
    # Fallback to ensure we have at least 3 reasons
    if len(reasons) < 3:
        reasons.append(f"Destination matches group purpose: {destination.get('best_for')}.")
        reasons.append(f"Comfortable family-friendliness score of {destination.get('family_friendliness')}/10.")
        reasons.append(f"Scenic and highly popular spots like {destination.get('top_activities', ['local spots'])[0]}.")
        
    return reasons[:5]


def generate_explainable_ai_reasons(
    destination_name: str,
    score: float,
    factor_scores: Dict[str, float],
    all_scores: Dict[str, float]
) -> str:
    """Generates the narrative explanation detailing why this was picked and why others ranked lower."""
    sorted_factors = sorted(factor_scores.items(), key=lambda x: x[1], reverse=True)
    strongest_factors = [f"{k.replace('_', ' ').title()} ({v:.0f}%)" for k, v in sorted_factors[:2]]
    strongest_str = " and ".join(strongest_factors)
    
    explanation = f"{destination_name} was selected as the top recommendation with a compatibility score of {score:.0f}%. "
    explanation += f"The strongest matching factors are {strongest_str}. "
    
    lower_dests = []
    for name, other_score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
        if name.lower() != destination_name.lower():
            lower_dests.append(f"{name} ({other_score:.0f}%)")
            
    if lower_dests:
        explanation += f"Other options ranked lower because they had less alignment with your group profile: {', '.join(lower_dests)}."
    else:
        explanation += "No other options were available for comparison."
        
    return explanation


def get_recommendations(request: GroupTripRequest) -> List[RecommendationDetails]:
    """Main entrypoint: analyzes all database destinations, scores, and ranks them."""
    destinations = get_all_destinations()
    if not destinations:
        return []
        
    all_scores = {}
    dest_factor_scores = {}
    
    # 1. First Pass: Calculate all factor scores and overall weighted scores
    for dest in destinations:
        dest_name = dest["name"]
        
        factor_scores = {
            "mood_match": calculate_mood_match(request.travelers, dest),
            "travel_purpose_match": calculate_travel_purpose_match(request.travelers, dest),
            "budget_suitability": calculate_budget_suitability(request.budget, request.days, request.travelers, dest),
            "vibe_match": calculate_vibe_match(request.preferred_vibe, dest),
            "age_suitability": calculate_age_suitability(request.travelers, dest),
            "medical_suitability": calculate_medical_suitability(request.travelers, dest),
            "activity_level_compatibility": calculate_activity_level_compatibility(request.travelers, dest),
            "food_preference_compatibility": calculate_food_preference_compatibility(request.travelers, dest),
        }
        
        overall_score = sum(factor_scores[f] * WEIGHTS[f] for f in WEIGHTS)
        
        # Round overall score
        all_scores[dest_name] = round(overall_score, 1)
        dest_factor_scores[dest_name] = factor_scores

    # 2. Second Pass: Build full recommendations
    results = []
    for dest in destinations:
        dest_name = dest["name"]
        score = all_scores[dest_name]
        factors = dest_factor_scores[dest_name]
        
        # Calculate expectation match
        exp_percentage, exp_summary = calculate_expectation_match(
    getattr(request, "preferred_vibe", ""),
    getattr(request, "priorities", []),
    getattr(request, "expectations", ""),
    dest
)
        
        exp_match = ExpectationMatchResponse(
            match_percentage=exp_percentage,
            summary=exp_summary
        )
        
        # Reasons
        reasons = generate_recommendation_reasons(
            request.preferred_vibe,
            request.priorities,
            dest,
            factors
        )
        
        # Warnings
        warnings = generate_smart_warnings(request, dest)
        
        # Explainable AI
        explanation = generate_explainable_ai_reasons(dest_name, score, factors, all_scores)
        
        rec = RecommendationDetails(
            destination=dest_name,
            compatibility_score=score,
            reasons=reasons,
            warnings=warnings,
            top_activities=dest.get("top_activities", []),
            expectation_match=exp_match,
            factor_scores=factors,
            score_explanation=explanation
        )
        results.append(rec)
        
    # Sort recommendations by compatibility score in descending order
    results.sort(key=lambda x: x.compatibility_score, reverse=True)
    return results
