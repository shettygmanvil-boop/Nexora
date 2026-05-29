import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.models.user import User
from app.volunteer_yatra.enums import ApplicationStatus, OpportunityStatus
from app.volunteer_yatra.models.application import VolunteerApplication
from app.volunteer_yatra.models.opportunity import VolunteerOpportunity
from app.volunteer_yatra.schemas.application import ApplicationCreate, ApplicationStatusUpdate
from app.volunteer_yatra.services.matching_service import compute_application_match_score
from app.volunteer_yatra.services.opportunity_service import get_opportunity
from app.volunteer_yatra.services.profile_service import get_or_create_volunteer_profile
from app.volunteer_yatra.utils.history import append_status_history


async def apply_to_opportunity(
    db: AsyncSession,
    user: User,
    opportunity_id: uuid.UUID,
    data: ApplicationCreate,
) -> VolunteerApplication:
    opp = await get_opportunity(db, opportunity_id)
    if opp.status != OpportunityStatus.PUBLISHED.value:
        raise HTTPException(status_code=400, detail="Opportunity is not open for applications")
    if opp.host_user_id == user.id:
        raise HTTPException(status_code=400, detail="Host cannot apply to own opportunity")

    existing = await db.execute(
        select(VolunteerApplication).where(
            VolunteerApplication.opportunity_id == opportunity_id,
            VolunteerApplication.volunteer_user_id == user.id,
            VolunteerApplication.status != ApplicationStatus.WITHDRAWN.value,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already applied to this opportunity")

    await get_or_create_volunteer_profile(db, user)
    match_score = await compute_application_match_score(db, user.id, opp)

    application = VolunteerApplication(
        opportunity_id=opportunity_id,
        volunteer_user_id=user.id,
        cover_message=data.cover_message,
        match_score=match_score,
        status=ApplicationStatus.PENDING.value,
        status_history=append_status_history([], ApplicationStatus.PENDING.value, user.id),
    )
    db.add(application)
    await db.flush()
    await db.refresh(application)
    return application


async def get_application(
    db: AsyncSession, application_id: uuid.UUID
) -> VolunteerApplication:
    result = await db.execute(
        select(VolunteerApplication).where(VolunteerApplication.id == application_id)
    )
    app = result.scalar_one_or_none()
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


async def list_volunteer_applications(
    db: AsyncSession, user_id: uuid.UUID
) -> list[VolunteerApplication]:
    result = await db.execute(
        select(VolunteerApplication)
        .where(VolunteerApplication.volunteer_user_id == user_id)
        .order_by(VolunteerApplication.created_at.desc())
    )
    return list(result.scalars().all())


async def list_host_applications(
    db: AsyncSession, host_user_id: uuid.UUID
) -> list[VolunteerApplication]:
    result = await db.execute(
        select(VolunteerApplication)
        .join(VolunteerOpportunity)
        .where(VolunteerOpportunity.host_user_id == host_user_id)
        .order_by(VolunteerApplication.created_at.desc())
    )
    return list(result.scalars().all())


async def update_application_status(
    db: AsyncSession,
    host_user: User,
    application_id: uuid.UUID,
    data: ApplicationStatusUpdate,
) -> VolunteerApplication:
    application = await get_application(db, application_id)
    opp = await get_opportunity(db, application.opportunity_id)
    if opp.host_user_id != host_user.id:
        raise HTTPException(status_code=403, detail="Only the host can review applications")

    new_status = data.status
    if new_status not in (
        ApplicationStatus.UNDER_REVIEW.value,
        ApplicationStatus.ACCEPTED.value,
        ApplicationStatus.REJECTED.value,
    ):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    application.status = new_status
    application.status_history = append_status_history(
        application.status_history or [],
        new_status,
        host_user.id,
        data.note,
    )
    await db.flush()
    await db.refresh(application)
    return application


async def withdraw_application(
    db: AsyncSession, user: User, application_id: uuid.UUID
) -> VolunteerApplication:
    application = await get_application(db, application_id)
    if application.volunteer_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your application")
    application.status = ApplicationStatus.WITHDRAWN.value
    application.status_history = append_status_history(
        application.status_history or [],
        ApplicationStatus.WITHDRAWN.value,
        user.id,
    )
    await db.flush()
    await db.refresh(application)
    return application
