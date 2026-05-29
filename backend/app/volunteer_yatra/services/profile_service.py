import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.models.user import User
from app.volunteer_yatra.models.host_profile import HostProfile
from app.volunteer_yatra.models.volunteer_profile import VolunteerProfile
from app.volunteer_yatra.schemas.profile import HostProfileUpdate, VolunteerProfileUpdate


async def get_or_create_volunteer_profile(
    db: AsyncSession, user: User
) -> VolunteerProfile:
    result = await db.execute(
        select(VolunteerProfile).where(VolunteerProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = VolunteerProfile(user_id=user.id)
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
    return profile


async def update_volunteer_profile(
    db: AsyncSession, user: User, data: VolunteerProfileUpdate
) -> VolunteerProfile:
    profile = await get_or_create_volunteer_profile(db, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.flush()
    await db.refresh(profile)
    return profile


async def get_or_create_host_profile(db: AsyncSession, user: User) -> HostProfile:
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = HostProfile(user_id=user.id)
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
    return profile


async def update_host_profile(
    db: AsyncSession, user: User, data: HostProfileUpdate
) -> HostProfile:
    profile = await get_or_create_host_profile(db, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.flush()
    await db.refresh(profile)
    return profile


async def get_host_profile_by_user(
    db: AsyncSession, user_id: uuid.UUID
) -> HostProfile | None:
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()
