from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.volunteer_yatra.schemas.common import ORMModel


class ReviewCreate(BaseModel):
    opportunity_id: UUID
    reviewee_id: UUID
    reviewer_role: str = Field(..., pattern="^(host|volunteer)$")
    rating: float = Field(..., ge=1, le=5)
    feedback: str | None = Field(None, max_length=2000)


class ReviewResponse(ORMModel):
    id: UUID
    opportunity_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    reviewer_role: str
    rating: float
    feedback: str | None
    created_at: datetime


class ReviewSummaryResponse(BaseModel):
    user_id: UUID
    average_rating: float
    review_count: int
    impact_score: float
