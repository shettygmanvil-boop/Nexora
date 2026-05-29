import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.platform.models.user import User
from app.volunteer_yatra.dependencies import get_current_user
from app.volunteer_yatra.schemas.application import ApplicationCreate, ApplicationResponse
from app.volunteer_yatra.schemas.opportunity import (
    OpportunityCreate,
    OpportunityListResponse,
    OpportunityResponse,
    OpportunityUpdate,
)
from app.volunteer_yatra.services import application_service, opportunity_service

router = APIRouter(prefix="/opportunities", tags=["Volunteer Opportunities"])


@router.get("", response_model=OpportunityListResponse)
async def list_opportunities(
    db: AsyncSession = Depends(get_db),
    skills: list[str] | None = Query(None),
    duration: str | None = None,
    is_remote: bool | None = None,
    food_included: bool | None = None,
    accommodation_included: bool | None = None,
    verified_host: bool | None = None,
    impact_category: str | None = None,
    status: str | None = "published",
    min_lat: float | None = None,
    max_lat: float | None = None,
    min_lng: float | None = None,
    max_lng: float | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    items, total = await opportunity_service.list_opportunities(
        db,
        skills=skills,
        duration=duration,
        is_remote=is_remote,
        food_included=food_included,
        accommodation_included=accommodation_included,
        verified_host=verified_host,
        impact_category=impact_category,
        status=status,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lng=min_lng,
        max_lng=max_lng,
        skip=skip,
        limit=limit,
    )
    return OpportunityListResponse(
        items=[OpportunityResponse.model_validate(i) for i in items],
        total=total,
    )


@router.post("", response_model=OpportunityResponse, status_code=201)
async def create_opportunity(
    data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    opp = await opportunity_service.create_opportunity(db, user, data)
    return OpportunityResponse.model_validate(opp)


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    opp = await opportunity_service.get_opportunity(db, opportunity_id)
    return OpportunityResponse.model_validate(opp)


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: uuid.UUID,
    data: OpportunityUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    opp = await opportunity_service.update_opportunity(db, user, opportunity_id, data)
    return OpportunityResponse.model_validate(opp)


@router.post("/{opportunity_id}/publish", response_model=OpportunityResponse)
async def publish_opportunity(
    opportunity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    opp = await opportunity_service.publish_opportunity(db, user, opportunity_id)
    return OpportunityResponse.model_validate(opp)


@router.post("/{opportunity_id}/apply", response_model=ApplicationResponse, status_code=201)
async def apply_to_opportunity(
    opportunity_id: uuid.UUID,
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    application = await application_service.apply_to_opportunity(
        db, user, opportunity_id, data
    )
    return ApplicationResponse.model_validate(application)
