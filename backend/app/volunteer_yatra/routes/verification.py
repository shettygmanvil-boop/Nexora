import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.platform.models.user import User
from app.volunteer_yatra.dependencies import get_current_user
from app.volunteer_yatra.schemas.verification import (
    VerificationCreate,
    VerificationModerate,
    VerificationResponse,
)
from app.volunteer_yatra.services import verification_service

router = APIRouter(prefix="/verification", tags=["Volunteer Verification"])


@router.post("", response_model=VerificationResponse, status_code=201)
async def request_verification(
    data: VerificationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    req = await verification_service.request_verification(db, user, data)
    return VerificationResponse.model_validate(req)


@router.get("", response_model=list[VerificationResponse])
async def list_verification_requests(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    status: str | None = Query(None),
):
    items = await verification_service.list_verification_requests(db, status=status)
    return [VerificationResponse.model_validate(i) for i in items]


@router.patch("/{request_id}", response_model=VerificationResponse)
async def moderate_verification(
    request_id: uuid.UUID,
    data: VerificationModerate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    req = await verification_service.moderate_verification(db, user, request_id, data)
    return VerificationResponse.model_validate(req)
