import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.models.user import User
from app.volunteer_yatra.enums import VerificationStatus, VerificationSubjectType
from app.volunteer_yatra.models.host_profile import HostProfile
from app.volunteer_yatra.models.verification import VerificationRequest
from app.volunteer_yatra.models.volunteer_profile import VolunteerProfile
from app.volunteer_yatra.schemas.verification import VerificationCreate, VerificationModerate
from app.volunteer_yatra.services.profile_service import (
    get_or_create_host_profile,
    get_or_create_volunteer_profile,
)


async def request_verification(
    db: AsyncSession, user: User, data: VerificationCreate
) -> VerificationRequest:
    if data.subject_type == VerificationSubjectType.VOLUNTEER.value:
        await get_or_create_volunteer_profile(db, user)
    else:
        await get_or_create_host_profile(db, user)

    existing = await db.execute(
        select(VerificationRequest).where(
            VerificationRequest.subject_user_id == user.id,
            VerificationRequest.subject_type == data.subject_type,
            VerificationRequest.status == VerificationStatus.PENDING.value,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Verification request already pending")

    req = VerificationRequest(
        subject_type=data.subject_type,
        subject_user_id=user.id,
        evidence_notes=data.evidence_notes,
    )
    db.add(req)
    await db.flush()
    await db.refresh(req)
    return req


async def moderate_verification(
    db: AsyncSession,
    moderator: User,
    request_id: uuid.UUID,
    data: VerificationModerate,
) -> VerificationRequest:
    result = await db.execute(
        select(VerificationRequest).where(VerificationRequest.id == request_id)
    )
    req = result.scalar_one_or_none()
    if req is None:
        raise HTTPException(status_code=404, detail="Verification request not found")

    req.status = data.status
    req.moderator_notes = data.moderator_notes
    req.moderated_by_id = moderator.id

    if data.status == VerificationStatus.VERIFIED.value:
        if req.subject_type == VerificationSubjectType.VOLUNTEER.value:
            vol_result = await db.execute(
                select(VolunteerProfile).where(
                    VolunteerProfile.user_id == req.subject_user_id
                )
            )
            profile = vol_result.scalar_one_or_none()
            if profile:
                profile.verification_status = VerificationStatus.VERIFIED.value
        else:
            host_result = await db.execute(
                select(HostProfile).where(HostProfile.user_id == req.subject_user_id)
            )
            host = host_result.scalar_one_or_none()
            if host:
                host.verification_status = VerificationStatus.VERIFIED.value
    elif data.status == VerificationStatus.REJECTED.value:
        if req.subject_type == VerificationSubjectType.VOLUNTEER.value:
            vol_result = await db.execute(
                select(VolunteerProfile).where(
                    VolunteerProfile.user_id == req.subject_user_id
                )
            )
            vol = vol_result.scalar_one_or_none()
            if vol:
                vol.verification_status = VerificationStatus.REJECTED.value
        else:
            host_result = await db.execute(
                select(HostProfile).where(HostProfile.user_id == req.subject_user_id)
            )
            host = host_result.scalar_one_or_none()
            if host:
                host.verification_status = VerificationStatus.REJECTED.value

    await db.flush()
    await db.refresh(req)
    return req


async def list_verification_requests(
    db: AsyncSession, status: str | None = None
) -> list[VerificationRequest]:
    query = select(VerificationRequest)
    if status:
        query = query.where(VerificationRequest.status == status)
    result = await db.execute(query.order_by(VerificationRequest.created_at.desc()))
    return list(result.scalars().all())
