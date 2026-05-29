"""
Maproom — Trip, Destinations, Itinerary, and Hotels Tests
==========================================================
Comprehensive async test suite covering:
  • Destinations Database query helpers
  • Trip Validation and Compatibility calculation logic
  • Destinations and Trip Planning API endpoints
  • Static Itinerary and Hotels placeholder endpoints
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database.destinations import (
    get_all_destinations,
    get_destination_by_name,
    get_destinations_by_vibe,
)
from app.schemas.trip import GroupTripRequest, Traveler


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_traveler_young() -> dict:
    return {
        "name": "Alice",
        "age": 28,
        "food_preference": "veg",
        "mood": "excited",
        "travel_purpose": "leisure",
        "medical_conditions": ["asthma"],
        "activity_level": "medium",
        "budget_preference": "standard",
    }


@pytest.fixture
def sample_traveler_senior() -> dict:
    return {
        "name": "Bob",
        "age": 65,
        "food_preference": "non-veg",
        "mood": "relaxed",
        "travel_purpose": "relaxation",
        "medical_conditions": ["hypertension", "knee pain"],
        "activity_level": "low",
        "budget_preference": "luxury",
    }


@pytest.fixture
async def async_client():
    """Async test client using ASGI transport (no real server needed)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


# ══════════════════════════════════════════════════════════════════════════════
# 1. Database Helper Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestDestinationsDatabase:

    def test_get_all_destinations(self):
        dests = get_all_destinations()
        assert len(dests) == 4
        names = {d["name"].lower() for d in dests}
        assert names == {"goa", "bangalore", "srinagar", "jaipur"}

    def test_get_destination_by_name_success(self):
        goa = get_destination_by_name("Goa")
        assert goa["name"] == "Goa"
        assert "beaches" in goa["vibes"]

        # Case-insensitivity and whitespace trimming
        bangalore = get_destination_by_name("  bangalore  ")
        assert bangalore["name"] == "Bangalore"

    def test_get_destination_by_name_missing_or_empty(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            get_destination_by_name("")
        with pytest.raises(ValueError, match="not found in the database"):
            get_destination_by_name("Atlantis")

    def test_get_destinations_by_vibe_success(self):
        # Explicit tag match
        beach_dests = get_destinations_by_vibe("beaches")
        assert len(beach_dests) == 1
        assert beach_dests[0]["name"] == "Goa"

        # Vibe-based high score match fallback (e.g. nightlife >= 7)
        nightlife_dests = get_destinations_by_vibe("nightlife")
        # Goa (9) and Bangalore (8) should match
        names = {d["name"] for d in nightlife_dests}
        assert "Goa" in names
        assert "Bangalore" in names

    def test_get_destinations_by_vibe_empty(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            get_destinations_by_vibe("  ")


# ══════════════════════════════════════════════════════════════════════════════
# 2. API Endpoint Integration Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestTripItineraryHotelsAPIEndpoints:

    @pytest.mark.asyncio
    async def test_get_destinations_endpoint(self, async_client):
        # Fetch all
        response = await async_client.get("/api/destinations")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

        # Fetch with vibe filter
        response = await async_client.get("/api/destinations", params={"vibe": "mountains"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Srinagar"

    @pytest.mark.asyncio
    async def test_get_destination_detail_endpoint_success(self, async_client):
        response = await async_client.get("/api/destinations/jaipur")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jaipur"
        assert data["weather_type"] == "Hot & Dry"
        assert "heritage" in data["vibes"]

    @pytest.mark.asyncio
    async def test_get_destination_detail_endpoint_not_found(self, async_client):
        response = await async_client.get("/api/destinations/Atlantis")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_itinerary_endpoint(self, async_client):
        response = await async_client.get("/api/itinerary")
        assert response.status_code == 200
        assert response.json() == {"message": "Itinerary endpoint"}

    @pytest.mark.asyncio
    async def test_hotels_endpoint(self, async_client):
        response = await async_client.get("/api/hotels")
        assert response.status_code == 200
        assert response.json() == {"message": "Hotels endpoint"}

    @pytest.mark.asyncio
    async def test_validate_trip_endpoint_success_preferred_dest(self, async_client, sample_traveler_young):
        payload = {
            "travelers": [sample_traveler_young],
            "budget": 30000.0,
            "days": 5,
            "preferred_vibe": "beaches",
            "priorities": ["relaxation", "sightseeing"],
            "destination_preference": "Goa",
            "expectations": "Looking for relaxation and beach strolls",
        }
        response = await async_client.post("/api/validate-trip", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["recommended_destination"] == "Goa"
        assert data["compatibility_score"] > 50.0
        assert len(data["reasons"]) > 0
        assert "Goa" in data["budget_summary"]
        # Young traveler with asthma in Goa -> no specific warning matching Goa in code (only warm climate warning)
        assert any("Climate warning" in w for w in data["warnings"])

    @pytest.mark.asyncio
    async def test_validate_trip_endpoint_unsupported_preferred_dest(self, async_client, sample_traveler_young):
        payload = {
            "travelers": [sample_traveler_young],
            "budget": 30000.0,
            "days": 5,
            "preferred_vibe": "beaches",
            "priorities": ["relaxation"],
            "destination_preference": "Atlantis",
        }
        response = await async_client.post("/api/validate-trip", json=payload)
        assert response.status_code == 400
        assert "not supported" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_validate_trip_endpoint_vibe_fallback(self, async_client, sample_traveler_young):
        # If no preferred destination is provided, vibe is used to match
        payload = {
            "travelers": [sample_traveler_young],
            "budget": 15000.0,
            "days": 3,
            "preferred_vibe": "mountains",
            "priorities": ["relaxation"],
        }
        response = await async_client.post("/api/validate-trip", json=payload)
        assert response.status_code == 200
        data = response.json()
        # "mountains" vibe matches Srinagar (has "mountains" in vibes)
        assert data["recommended_destination"] == "Srinagar"

    @pytest.mark.asyncio
    async def test_validate_trip_endpoint_compatibility_calculations(
        self, async_client, sample_traveler_young, sample_traveler_senior
    ):
        # Has senior traveler (age 65) -> senior friendliness check
        # Destination Goa has senior_citizen_friendliness = 5 (less than 7), which deducts 10.0 points
        payload = {
            "travelers": [sample_traveler_young, sample_traveler_senior],
            "budget": 100000.0,
            "days": 4,
            "preferred_vibe": "beaches",
            "priorities": ["relaxation"],
            "destination_preference": "Goa",
        }
        response = await async_client.post("/api/validate-trip", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["compatibility_score"] <= 100.0
        
        # Verify medical warnings generated
        warnings = data["warnings"]
        # Goa has medical risk notes: "Dehydration risk under high heat index. Ensure hydration for elderly and children."
        # Alice (asthma) -> warning: "Medical warning for Alice (asthma): Dehydration risk..."
        # Bob (hypertension) -> warning: "Medical warning for Bob (hypertension): Dehydration..."
        # Bob (knee pain) -> warning: "Medical warning for Bob (knee pain): Dehydration..."
        assert any("Alice" in w and "asthma" in w for w in warnings)
        assert any("Bob" in w and "hypertension" in w for w in warnings)
        assert any("Bob" in w and "knee pain" in w for w in warnings)
