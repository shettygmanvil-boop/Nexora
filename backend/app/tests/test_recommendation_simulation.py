"""
Maproom — Recommendation and Simulation System Tests
=====================================================
Comprehensive async test suite covering:
  • Unit tests for recommendation scoring services
  • GET/POST endpoints for recommendations
  • Budget simulation and slider change adjustment service
  • Mocked CrewAI simulation endpoints (budget, conflict resolution, solo split, upgrade, dynamic)
"""

import json
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock

from app.main import app
from app.schemas.travel import TravelerProfile, TravelGroupRequest
from app.schemas.trip import GroupTripRequest, Traveler
from app.services.recommendation_service import (
    calculate_mood_match,
    calculate_travel_purpose_match,
    calculate_age_suitability,
    calculate_food_preference_compatibility,
    calculate_medical_suitability,
    calculate_budget_suitability,
    calculate_vibe_match,
    calculate_activity_level_compatibility,
    calculate_expectation_match,
    generate_smart_warnings,
    generate_recommendation_reasons,
    generate_explainable_ai_reasons,
    get_recommendations,
)
from app.services.simulation import simulate_budget_adjustment


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
async def async_client():
    """Async test client using ASGI transport (no real server needed)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def destinations_mock_data():
    return {
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
            "top_activities": ["Scuba Diving at Grande Island", "Anjuna Beach Sunset & Night Market"],
            "vibes": ["beaches", "nightlife", "adventure", "coastal", "relaxation"]
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
            "medical_risk_notes": "Cold weather and high altitude risk. Asthma and heart patients should carry warm wear.",
            "top_activities": ["Shikara Ride on Dal Lake", "Gulmarg Gondola Ride"],
            "vibes": ["cold", "mountains", "scenic", "spirituality", "nature", "relaxation"]
        }
    }


# ══════════════════════════════════════════════════════════════════════════════
# 1. Recommendation Service Unit Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestRecommendationServiceUnit:

    def test_mood_match(self, destinations_mock_data):
        # Relaxed traveler matched against peacefulness_score of Srinagar (9)
        t_relaxed = Traveler(name="Alice", age=30, mood="relaxed", travel_purpose="leisure")
        score_srinagar = calculate_mood_match([t_relaxed], destinations_mock_data["srinagar"])
        assert score_srinagar == 90.0

        # Adventurous traveler matched against adventure_score of Goa (8)
        t_adv = Traveler(name="Bob", age=30, mood="adventurous", travel_purpose="leisure")
        score_goa = calculate_mood_match([t_adv], destinations_mock_data["goa"])
        assert score_goa == 80.0

    def test_travel_purpose_match(self, destinations_mock_data):
        t_nature = Traveler(name="Alice", age=30, mood="chill", travel_purpose="nature exploration")
        score = calculate_travel_purpose_match([t_nature], destinations_mock_data["srinagar"])
        assert score == 100.0

        t_work = Traveler(name="Bob", age=30, mood="chill", travel_purpose="workcation")
        # Srinagar isn't primary workcation vibe, has cold weather, so fallback score is computed
        score_srinagar = calculate_travel_purpose_match([t_work], destinations_mock_data["srinagar"])
        assert score_srinagar == 60.0

    def test_age_suitability(self, destinations_mock_data):
        # Senior citizen in Goa: senior friendliness = 5, high crowd level -> penalties applied
        t_senior = Traveler(name="Gran", age=72, mood="chill", travel_purpose="relaxation")
        score_goa = calculate_age_suitability([t_senior], destinations_mock_data["goa"])
        # senior friendliness * 10 - 10 (crowd) - 15 (nightlife) = 50 - 10 - 15 = 25
        assert score_goa == 25.0

        # Child in Srinagar: family friendliness = 9 -> high score
        t_child = Traveler(name="Kid", age=8, mood="excited", travel_purpose="leisure")
        score_srinagar = calculate_age_suitability([t_child], destinations_mock_data["srinagar"])
        assert score_srinagar == 90.0

    def test_food_preference_compatibility(self, destinations_mock_data):
        t_veg = Traveler(name="Alice", age=30, food_preference="veg")
        # Goa has medium veg availability -> 80
        score_goa = calculate_food_preference_compatibility([t_veg], destinations_mock_data["goa"])
        assert score_goa == 80.0

        t_nonveg = Traveler(name="Bob", age=30, food_preference="non-veg")
        score_goa_nv = calculate_food_preference_compatibility([t_nonveg], destinations_mock_data["goa"])
        assert score_goa_nv == 95.0

    def test_medical_suitability(self, destinations_mock_data):
        # Asthma traveler in Cold weather (Srinagar) -> score penalty
        t_asthma = Traveler(name="Alice", age=30, medical_conditions=["asthma"])
        score_srinagar = calculate_medical_suitability([t_asthma], destinations_mock_data["srinagar"])
        assert score_srinagar == 60.0

        # Knee pain in high adventure destination (Goa, adventure=8 >= 7) -> penalty
        t_knee = Traveler(name="Bob", age=30, medical_conditions=["knee pain"])
        score_goa = calculate_medical_suitability([t_knee], destinations_mock_data["goa"])
        assert score_goa == 70.0

    def test_budget_suitability(self, destinations_mock_data):
        t_budget = Traveler(name="Alice", age=30, budget_preference="budget")
        # Avg budget/day = 10000 / (4 * 1) = 2500 (<3000). Goa budget friendliness = 7 -> score 70.0
        score_goa = calculate_budget_suitability(10000.0, 4, [t_budget], destinations_mock_data["goa"])
        assert score_goa == 70.0

    def test_vibe_match(self, destinations_mock_data):
        score_match = calculate_vibe_match("beaches", destinations_mock_data["goa"])
        assert score_match == 100.0

        score_fallback = calculate_vibe_match("peaceful", destinations_mock_data["srinagar"])
        assert score_fallback == 85.0

        score_mismatch = calculate_vibe_match("nightlife", destinations_mock_data["srinagar"])
        # Srinagar nightlife score is 2 (<7), no direct vibe tag -> 40.0
        assert score_mismatch == 40.0

    def test_activity_level_compatibility(self, destinations_mock_data):
        t_high = Traveler(name="Alice", age=30, activity_level="high")
        score_goa = calculate_activity_level_compatibility([t_high], destinations_mock_data["goa"])
        assert score_goa == 80.0

        t_low = Traveler(name="Bob", age=30, activity_level="low")
        score_srinagar = calculate_activity_level_compatibility([t_low], destinations_mock_data["srinagar"])
        # (peacefulness (9) + senior citizen (7)) / 2 * 10 = 80.0
        assert score_srinagar == 80.0

    def test_expectation_match(self, destinations_mock_data):
        score, summary = calculate_expectation_match(
            "beaches", ["party", "food"], "I want beaches and a night party", destinations_mock_data["goa"]
        )
        assert score > 70.0
        assert "beaches" in summary.lower()

    def test_generate_smart_warnings(self):
        req = GroupTripRequest(
            travelers=[
                Traveler(name="Alice", age=25, medical_conditions=["asthma"]),
                Traveler(name="Bob", age=68, medical_conditions=["hypertension"]),
            ],
            budget=2000.0, # extremely low budget
            days=5,
            preferred_vibe="beaches",
            priorities=["party"],
        )
        dest = {
            "name": "Goa",
            "weather_type": "Warm & Humid",
            "crowd_level": "High",
            "nightlife_score": 9,
            "adventure_score": 8,
            "budget_friendliness": 7,
        }
        warnings = generate_smart_warnings(req, dest)
        # Dehydration warning for hypertension in Warm & Humid climate
        assert any("hypertension" in w and "dehydration" in w for w in warnings)
        # Low budget + luxury preference mismatch check?
        # Senior citizen + high crowd & nightlife check
        assert any("senior citizen" in w and "nightlife" in w for w in warnings)

    def test_generate_recommendation_reasons(self, destinations_mock_data):
        reasons = generate_recommendation_reasons(
            "beaches", ["party"], destinations_mock_data["goa"],
            {"vibe_match": 100.0, "food_preference_compatibility": 80.0, "activity_level_compatibility": 80.0, "budget_suitability": 85.0}
        )
        assert len(reasons) >= 3
        assert any("beaches" in r for r in reasons)

    def test_generate_explainable_ai_reasons(self):
        factors = {"vibe_match": 90.0, "mood_match": 80.0}
        all_scores = {"Goa": 85.0, "Srinagar": 70.0}
        explanation = generate_explainable_ai_reasons("Goa", 85.0, factors, all_scores)
        assert "Goa" in explanation
        assert "Srinagar" in explanation


# ══════════════════════════════════════════════════════════════════════════════
# 2. Recommendation Engine Route Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestRecommendationAPIEndpoints:

    @pytest.mark.asyncio
    async def test_recommendation_destinations(self, async_client):
        response = await async_client.get("/api/recommendation/destinations")
        assert response.status_code == 200
        data = response.json()
        assert set(data) == {"bangalore", "goa", "srinagar", "jaipur"}

    @pytest.mark.asyncio
    async def test_post_recommendation_root_fallback(self, async_client):
        # Tests the LLM-fallback route (triggers generate_mock_recommendation when no LLM key exists)
        payload = {
            "travelers": [
                {
                    "name": "Jane",
                    "age": 29,
                    "medical_conditions": ["asthma"],
                    "vibe_preference": "cold",
                    "accommodation_preference": "standard",
                    "travel_style": "relaxation",
                    "travel_purpose": "relaxation",
                }
            ],
            "total_budget": 50000.0,
            "num_days": 4,
            "expectations": "Peaceful snow views and lakes",
        }
        response = await async_client.post("/api/recommendation/", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Vibe "cold" should map fallback choice to Srinagar
        assert data["destination_name"] == "Srinagar"
        assert data["group_compatibility_score"] > 0
        assert "budget_analysis" in data
        assert "weather_health_safety" in data
        assert any("asthma" in w.lower() for w in data["weather_health_safety"]["health_warnings"])

    @pytest.mark.asyncio
    async def test_post_recommend_ranked(self, async_client):
        # Tests the offline recommendation engine route
        payload = {
            "travelers": [
                {
                    "name": "Alice",
                    "age": 28,
                    "food_preference": "veg",
                    "mood": "excited",
                    "travel_purpose": "leisure",
                    "medical_conditions": [],
                    "activity_level": "medium",
                    "budget_preference": "standard",
                }
            ],
            "budget": 60000.0,
            "days": 4,
            "preferred_vibe": "beaches",
            "priorities": ["sightseeing", "relaxation"],
            "expectations": "Beaches and fun",
        }
        response = await async_client.post("/api/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        # Top one should be Goa because vibe is beaches
        assert data[0]["destination"] == "Goa"
        assert data[0]["compatibility_score"] >= data[1]["compatibility_score"]


# ══════════════════════════════════════════════════════════════════════════════
# 3. Simulation Service & Route Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestSimulationServiceAndAPI:

    def test_simulate_budget_adjustment_service(self):
        travelers = [TravelerProfile(
            name="Alice", age=30, vibe_preference="beaches", accommodation_preference="standard"
        )]
        # Low budget -> Economy hotel recommended, warning alerts
        response_low = simulate_budget_adjustment("goa", 5000.0, 3, travelers)
        assert response_low.updated_budget_allocation.accommodation_cost == 2250.0
        assert any("budget" in change.lower() or "backpacker" in change.lower() for change in response_low.itinerary_changes)

        # High budget -> Upgrades unlocked
        response_high = simulate_budget_adjustment("goa", 150000.0, 3, travelers)
        assert response_high.updated_budget_allocation.accommodation_cost == 67500.0
        assert "All available upgrades unlocked!" in response_high.suggested_upgrades

    @pytest.mark.asyncio
    async def test_post_recommendation_simulate_endpoint(self, async_client):
        payload = {
            "destination": "Goa",
            "target_budget": 45000.0,
            "num_days": 4,
            "travelers": [
                {
                    "name": "Jane",
                    "age": 29,
                    "vibe_preference": "beaches",
                    "medical_conditions": [],
                }
            ],
        }
        response = await async_client.post(
            "/api/recommendation/simulate",
            params={
                "destination": payload["destination"],
                "target_budget": payload["target_budget"],
                "num_days": payload["num_days"],
            },
            json=payload["travelers"],
        )
        assert response.status_code == 200
        data = response.json()
        assert "updated_budget_allocation" in data
        assert "compatibility_score" in data

    @pytest.mark.asyncio
    @patch("app.api.routes.simulation.Crew")
    async def test_run_budget_simulation_endpoint(self, mock_crew_class, async_client):
        # Mock Crew kickoff_async
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff_async = AsyncMock(
            return_str='{"optimized_budget": 45000, "explanation": "Successfully optimized budget"}'
        )
        # Setting up __str__ for the returned value from kickoff_async so parse_crew_json parses it
        mock_crew_instance.kickoff_async.return_value = '{"optimized_budget": 45000, "explanation": "Successfully optimized budget"}'
        mock_crew_class.return_value = mock_crew_instance

        payload = {
            "total_budget": 50000.0,
            "traveler_count": 3,
            "demographic_notes": "Active adults",
            "budget_slider_value": {"lodging": 50, "activities": 30, "food": 20},
        }
        response = await async_client.post("/api/run-budget-simulation", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["optimized_budget"] == 45000

    @pytest.mark.asyncio
    @patch("app.api.routes.simulation.Crew")
    async def test_run_conflict_resolution_endpoint(self, mock_crew_class, async_client):
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff_async = AsyncMock(
            return_value='{"compromise_itinerary": "Beaches in morning, Temples in afternoon"}'
        )
        mock_crew_class.return_value = mock_crew_instance

        payload = {
            "traveler_profiles": [{"name": "Teen", "vibe": "beaches"}, {"name": "Parent", "vibe": "temples"}],
            "trip_context": "Goa trip",
            "sub_groups": ["Teenagers", "Parents"],
        }
        response = await async_client.post("/api/conflict-resolution", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["compromise_itinerary"] == "Beaches in morning, Temples in afternoon"

    @pytest.mark.asyncio
    @patch("app.api.routes.simulation.Crew")
    async def test_group_solo_split_endpoint(self, mock_crew_class, async_client):
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff_async = AsyncMock(
            return_value='{"group_tracks": [], "solo_tracks": [], "reunion": "dinner"}'
        )
        mock_crew_class.return_value = mock_crew_instance

        payload = {
            "traveler_profiles": [{"name": "Alice"}, {"name": "Bob"}],
            "trip_context": "Goa trip",
            "sub_groups": ["Group A", "Group B"],
        }
        response = await async_client.post("/api/group-solo-split", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["reunion"] == "dinner"

    @pytest.mark.asyncio
    @patch("app.api.routes.simulation.Crew")
    async def test_smart_budget_expand_endpoint(self, mock_crew_class, async_client):
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff_async = AsyncMock(
            return_value='{"options": ["Upgrade hotel to 5-star"], "cost": 15000}'
        )
        mock_crew_class.return_value = mock_crew_instance

        payload = {
            "total_budget": 60000.0,
            "traveler_count": 2,
            "demographic_notes": "Couple",
            "budget_slider_value": {"accommodation": 60},
        }
        response = await async_client.post("/api/smart-budget-expand", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["cost"] == 15000

    @pytest.mark.asyncio
    @patch("app.api.routes.simulation.Crew")
    async def test_dynamic_simulate_endpoint(self, mock_crew_class, async_client):
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff_async = AsyncMock(
            return_value='{"impact": "Weather change calls for indoor museum replacement", "cost_delta": 0}'
        )
        mock_crew_class.return_value = mock_crew_instance

        payload = {
            "original_plan": {"day1": "beach walk"},
            "parameter_changes": {"weather": "heavy rain"},
        }
        response = await async_client.post("/api/dynamic-simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["cost_delta"] == 0
