from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.volunteer_yatra.schemas.common import ORMModel


class VerificationCreate(BaseModel):
    subject_type: str = Field(..., pattern="^(host|volunteer)$")
    evidence_notes: str | None = Field(None, max_length=2000)


class VerificationModerate(BaseModel):
    status: str = Field(..., pattern="^(verified|rejected)$")
    moderator_notes: str | None = None


class VerificationResponse(ORMModel):
    id: UUID
    subject_type: str
    subject_user_id: UUID
    status: str
    evidence_notes: str | None
    moderator_notes: str | None
    moderated_by_id: UUID | None
    created_at: datetime
    updated_at: datetime
