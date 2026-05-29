import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.platform.models.user import User
from app.volunteer_yatra.dependencies import get_current_user
from app.volunteer_yatra.schemas.agent import (
    ImpactNarrativeResponse,
    MatchRequest,
    MatchResponse,
    RecommendationResponse,
    SafetyCheckRequest,
    SafetyCheckResponse,
)
from app.volunteer_yatra.services import agent_orchestrator

router = APIRouter(prefix="/agents", tags=["Volunteer AI Agents"])


@router.post("/match", response_model=MatchResponse)
async def run_matching(
    data: MatchRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await agent_orchestrator.run_matching(
        db, user, opportunity_id=data.opportunity_id, limit=data.limit
    )


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = 10,
):
    return await agent_orchestrator.run_recommendations(db, user, limit=limit)


@router.post("/safety-check", response_model=SafetyCheckResponse)
async def safety_check(
    data: SafetyCheckRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await agent_orchestrator.run_safety_check(
        db,
        opportunity_id=data.opportunity_id,
        title=data.title,
        description=data.description,
    )


@router.get("/impact-narrative", response_model=ImpactNarrativeResponse)
async def impact_narrative(db: AsyncSession = Depends(get_db)):
    return await agent_orchestrator.run_impact_narrative(db)
