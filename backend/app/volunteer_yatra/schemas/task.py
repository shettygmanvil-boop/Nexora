from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.volunteer_yatra.schemas.common import ORMModel


class TaskCreate(BaseModel):
    opportunity_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    assigned_user_id: UUID | None = None
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    assigned_user_id: UUID | None = None
    status: str | None = Field(
        None, pattern="^(pending|in_progress|completed|cancelled)$"
    )
    due_date: date | None = None


class TaskResponse(ORMModel):
    id: UUID
    opportunity_id: UUID
    room_id: UUID | None
    title: str
    description: str | None
    assigned_user_id: UUID | None
    status: str
    due_date: date | None
    created_at: datetime
    updated_at: datetime
