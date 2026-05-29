from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.volunteer_yatra.schemas.common import ORMModel, StatusHistoryEntry


class ApplicationCreate(BaseModel):
    cover_message: str | None = Field(None, max_length=2000)


class ApplicationStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(under_review|accepted|rejected)$")
    note: str | None = None


class ApplicationResponse(ORMModel):
    id: UUID
    opportunity_id: UUID
    volunteer_user_id: UUID
    status: str
    cover_message: str | None
    match_score: float | None
    status_history: list[StatusHistoryEntry]
    created_at: datetime
    updated_at: datetime


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
