import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.platform.models.user import User
from app.volunteer_yatra.dependencies import get_current_user
from app.volunteer_yatra.schemas.review import ReviewCreate, ReviewResponse, ReviewSummaryResponse
from app.volunteer_yatra.services import review_service

router = APIRouter(prefix="/reviews", tags=["Volunteer Reviews"])


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    review = await review_service.create_review(db, user, data)
    return ReviewResponse.model_validate(review)


@router.get("/summary/{user_id}", response_model=ReviewSummaryResponse)
async def get_review_summary(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await review_service.get_review_summary(db, user_id)
