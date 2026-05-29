"""
Volunteer Yatra API integration tests.
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import init_db
from app.main import app

HOST_ID = str(uuid.uuid4())
VOLUNTEER_ID = str(uuid.uuid4())


@pytest.fixture
async def client():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def host_headers():
    return {"X-Dev-User-Id": HOST_ID, "X-Dev-User-Email": f"host-{HOST_ID}@test.local"}


def volunteer_headers():
    return {"X-Dev-User-Id": VOLUNTEER_ID, "X-Dev-User-Email": f"volunteer-{VOLUNTEER_ID}@test.local"}


@pytest.mark.asyncio
async def test_volunteer_flow(client: AsyncClient):
    # Host profile
    resp = await client.put(
        "/api/volunteer-yatra/profiles/host/me",
        json={"organization_name": "Green Earth NGO", "bio": "Community host"},
        headers=host_headers(),
    )
    assert resp.status_code == 200

    # Create opportunity
    resp = await client.post(
        "/api/volunteer-yatra/opportunities",
        json={
            "title": "Beach Cleanup Drive",
            "description": "Join us for a coastal conservation volunteer day with training provided.",
            "latitude": 15.2993,
            "longitude": 74.124,
            "location_name": "Goa",
            "skills_required": ["teamwork", "environment"],
            "duration": "1 day",
            "impact_category": "environment",
            "capacity": 10,
        },
        headers=host_headers(),
    )
    assert resp.status_code == 201
    opp = resp.json()
    opp_id = opp["id"]

    # Publish
    resp = await client.post(
        f"/api/volunteer-yatra/opportunities/{opp_id}/publish",
        headers=host_headers(),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"
    assert resp.json()["room_id"] is not None

    # List published
    resp = await client.get("/api/volunteer-yatra/opportunities")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # Volunteer profile + apply
    await client.put(
        "/api/volunteer-yatra/profiles/volunteer/me",
        json={
            "skills": ["teamwork", "environment"],
            "interests": ["environment"],
        },
        headers=volunteer_headers(),
    )

    resp = await client.post(
        f"/api/volunteer-yatra/opportunities/{opp_id}/apply",
        json={"cover_message": "Excited to help!"},
        headers=volunteer_headers(),
    )
    assert resp.status_code == 201
    assert resp.json()["match_score"] is not None
    app_id = resp.json()["id"]

    # Host accepts
    resp = await client.patch(
        f"/api/volunteer-yatra/applications/{app_id}",
        json={"status": "accepted", "note": "Welcome aboard"},
        headers=host_headers(),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"

    # Matching agent
    resp = await client.post(
        "/api/volunteer-yatra/agents/match",
        json={"limit": 5},
        headers=volunteer_headers(),
    )
    assert resp.status_code == 200
    assert len(resp.json()["matches"]) >= 1

    # Impact summary
    resp = await client.get("/api/volunteer-yatra/impact/summary")
    assert resp.status_code == 200
    assert "volunteer_hours" in resp.json()


@pytest.mark.asyncio
async def test_travel_health_unchanged(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
