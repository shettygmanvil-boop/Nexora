import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.platform.models.user import User
from app.volunteer_yatra.dependencies import get_current_user
from app.volunteer_yatra.schemas.application import (
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationStatusUpdate,
)
from app.volunteer_yatra.services import application_service

router = APIRouter(prefix="/applications", tags=["Volunteer Applications"])


@router.get("", response_model=ApplicationListResponse)
async def list_my_applications(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = await application_service.list_volunteer_applications(db, user.id)
    return ApplicationListResponse(
        items=[ApplicationResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get("/host", response_model=ApplicationListResponse)
async def list_host_applications(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = await application_service.list_host_applications(db, user.id)
    return ApplicationListResponse(
        items=[ApplicationResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app = await application_service.get_application(db, application_id)
    return ApplicationResponse.model_validate(app)


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application_status(
    application_id: uuid.UUID,
    data: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app = await application_service.update_application_status(db, user, application_id, data)
    return ApplicationResponse.model_validate(app)


@router.post("/{application_id}/withdraw", response_model=ApplicationResponse)
async def withdraw_application(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app = await application_service.withdraw_application(db, user, application_id)
    return ApplicationResponse.model_validate(app)
