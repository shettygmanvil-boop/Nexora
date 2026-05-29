from uuid import UUID

from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    opportunity_id: UUID | None = None
    limit: int = Field(default=10, ge=1, le=50)


class MatchResult(BaseModel):
    opportunity_id: UUID
    match_score: float
    reasons: list[str]


class MatchResponse(BaseModel):
    matches: list[MatchResult]


class RecommendationResponse(BaseModel):
    opportunity_ids: list[UUID]
    summaries: list[str]


class SafetyCheckRequest(BaseModel):
    opportunity_id: UUID | None = None
    title: str | None = None
    description: str | None = None


class SafetyCheckResponse(BaseModel):
    risk_level: str
    flags: list[str]
    moderation_recommendation: str


class ImpactNarrativeResponse(BaseModel):
    summary: str
    highlights: list[str]
