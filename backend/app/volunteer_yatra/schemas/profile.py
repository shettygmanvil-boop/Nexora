from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.volunteer_yatra.schemas.common import ORMModel


class VolunteerProfileUpdate(BaseModel):
    skills: list[str] | None = None
    languages: list[str] | None = None
    availability: dict | None = None
    interests: list[str] | None = None
    portfolio_links: list[str] | None = None


class VolunteerProfileResponse(ORMModel):
    id: UUID
    user_id: UUID
    skills: list[str]
    languages: list[str]
    availability: dict | None
    interests: list[str]
    portfolio_links: list[str]
    volunteer_hours: float
    completed_projects: int
    impact_score: float
    verification_status: str
    created_at: datetime
    updated_at: datetime


class HostProfileUpdate(BaseModel):
    organization_name: str | None = None
    organization_id: UUID | None = None
    bio: str | None = None
    skills_needed: list[str] | None = None


class HostProfileResponse(ORMModel):
    id: UUID
    user_id: UUID
    organization_id: UUID | None
    organization_name: str | None
    bio: str | None
    skills_needed: list[str]
    verification_status: str
    impact_score: float
    rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime
