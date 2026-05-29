from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.platform.models.user import User
from app.volunteer_yatra.dependencies import get_current_user
from app.volunteer_yatra.schemas.profile import (
    HostProfileResponse,
    HostProfileUpdate,
    VolunteerProfileResponse,
    VolunteerProfileUpdate,
)
from app.volunteer_yatra.services import profile_service

router = APIRouter(prefix="/profiles", tags=["Volunteer Profiles"])


@router.get("/volunteer/me", response_model=VolunteerProfileResponse)
async def get_volunteer_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = await profile_service.get_or_create_volunteer_profile(db, user)
    return VolunteerProfileResponse.model_validate(profile)


@router.put("/volunteer/me", response_model=VolunteerProfileResponse)
async def update_volunteer_profile(
    data: VolunteerProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = await profile_service.update_volunteer_profile(db, user, data)
    return VolunteerProfileResponse.model_validate(profile)


@router.get("/host/me", response_model=HostProfileResponse)
async def get_host_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = await profile_service.get_or_create_host_profile(db, user)
    return HostProfileResponse.model_validate(profile)


@router.put("/host/me", response_model=HostProfileResponse)
async def update_host_profile(
    data: HostProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = await profile_service.update_host_profile(db, user, data)
    return HostProfileResponse.model_validate(profile)
