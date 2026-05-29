import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.models.user import User
from app.volunteer_yatra.enums import OpportunityStatus
from app.volunteer_yatra.models.opportunity import VolunteerOpportunity
from app.volunteer_yatra.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.volunteer_yatra.services.profile_service import get_or_create_host_profile
from app.volunteer_yatra.services.room_bridge import create_volunteer_room


async def create_opportunity(
    db: AsyncSession, user: User, data: OpportunityCreate
) -> VolunteerOpportunity:
    await get_or_create_host_profile(db, user)
    opp = VolunteerOpportunity(host_user_id=user.id, **data.model_dump())
    db.add(opp)
    await db.flush()
    await db.refresh(opp)
    return opp


async def get_opportunity(db: AsyncSession, opportunity_id: uuid.UUID) -> VolunteerOpportunity:
    result = await db.execute(
        select(VolunteerOpportunity).where(VolunteerOpportunity.id == opportunity_id)
    )
    opp = result.scalar_one_or_none()
    if opp is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp


async def update_opportunity(
    db: AsyncSession,
    user: User,
    opportunity_id: uuid.UUID,
    data: OpportunityUpdate,
) -> VolunteerOpportunity:
    opp = await get_opportunity(db, opportunity_id)
    if opp.host_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not the host of this opportunity")
    if opp.status == OpportunityStatus.CLOSED.value:
        raise HTTPException(status_code=400, detail="Cannot update a closed opportunity")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(opp, field, value)
    await db.flush()
    await db.refresh(opp)
    return opp


async def publish_opportunity(
    db: AsyncSession, user: User, opportunity_id: uuid.UUID
) -> VolunteerOpportunity:
    opp = await get_opportunity(db, opportunity_id)
    if opp.host_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not the host of this opportunity")
    if opp.status == OpportunityStatus.PUBLISHED.value:
        return opp
    if opp.room_id is None:
        await create_volunteer_room(db, opp, user.id)
    opp.status = OpportunityStatus.PUBLISHED.value
    opp.published_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(opp)
    return opp


async def list_opportunities(
    db: AsyncSession,
    *,
    skills: list[str] | None = None,
    duration: str | None = None,
    is_remote: bool | None = None,
    food_included: bool | None = None,
    accommodation_included: bool | None = None,
    verified_host: bool | None = None,
    impact_category: str | None = None,
    status: str | None = OpportunityStatus.PUBLISHED.value,
    min_lat: float | None = None,
    max_lat: float | None = None,
    min_lng: float | None = None,
    max_lng: float | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[VolunteerOpportunity], int]:
    from app.volunteer_yatra.models.host_profile import HostProfile

    query = select(VolunteerOpportunity)
    count_query = select(func.count()).select_from(VolunteerOpportunity)
    filters = []

    if status:
        filters.append(VolunteerOpportunity.status == status)
    if duration:
        filters.append(VolunteerOpportunity.duration == duration)
    if is_remote is not None:
        filters.append(VolunteerOpportunity.is_remote == is_remote)
    if food_included is not None:
        filters.append(VolunteerOpportunity.food_included == food_included)
    if accommodation_included is not None:
        filters.append(VolunteerOpportunity.accommodation_included == accommodation_included)
    if impact_category:
        filters.append(VolunteerOpportunity.impact_category == impact_category)
    if min_lat is not None:
        filters.append(VolunteerOpportunity.latitude >= min_lat)
    if max_lat is not None:
        filters.append(VolunteerOpportunity.latitude <= max_lat)
    if min_lng is not None:
        filters.append(VolunteerOpportunity.longitude >= min_lng)
    if max_lng is not None:
        filters.append(VolunteerOpportunity.longitude <= max_lng)

    if verified_host:
        query = query.join(
            HostProfile, HostProfile.user_id == VolunteerOpportunity.host_user_id
        )
        count_query = count_query.join(
            HostProfile, HostProfile.user_id == VolunteerOpportunity.host_user_id
        )
        filters.append(HostProfile.verification_status == "verified")

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        query.order_by(VolunteerOpportunity.created_at.desc()).offset(skip).limit(limit)
    )
    items = list(result.scalars().all())

    if skills:
        skill_set = {s.lower() for s in skills}
        items = [
            o
            for o in items
            if skill_set.intersection({s.lower() for s in (o.skills_required or [])})
            or not o.skills_required
        ]
        total = len(items)

    return items, total
