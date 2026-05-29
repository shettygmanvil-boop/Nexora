from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.volunteer_yatra.schemas.common import ORMModel


class OpportunityCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_name: str | None = None
    skills_required: list[str] = Field(default_factory=list)
    duration: str = "flexible"
    is_remote: bool = False
    food_included: bool = False
    accommodation_included: bool = False
    impact_category: str = Field(..., min_length=2, max_length=64)
    capacity: int = Field(default=1, ge=1, le=500)


class OpportunityUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = Field(None, min_length=10)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    location_name: str | None = None
    skills_required: list[str] | None = None
    duration: str | None = None
    is_remote: bool | None = None
    food_included: bool | None = None
    accommodation_included: bool | None = None
    impact_category: str | None = None
    capacity: int | None = Field(None, ge=1, le=500)


class OpportunityResponse(ORMModel):
    id: UUID
    host_user_id: UUID
    room_id: UUID | None
    title: str
    description: str
    latitude: float
    longitude: float
    location_name: str | None
    skills_required: list[str]
    duration: str
    is_remote: bool
    food_included: bool
    accommodation_included: bool
    impact_category: str
    capacity: int
    status: str
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None


class OpportunityListResponse(BaseModel):
    items: list[OpportunityResponse]
    total: int
