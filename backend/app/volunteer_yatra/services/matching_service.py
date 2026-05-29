import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.models.user import User
from app.volunteer_yatra.enums import OpportunityStatus
from app.volunteer_yatra.models.opportunity import VolunteerOpportunity
from app.volunteer_yatra.models.volunteer_profile import VolunteerProfile
from app.volunteer_yatra.schemas.agent import MatchResult
from app.volunteer_yatra.services.profile_service import get_or_create_volunteer_profile
from app.volunteer_yatra.utils.scoring import compute_match_score


async def compute_application_match_score(
    db: AsyncSession,
    volunteer_user_id: uuid.UUID,
    opportunity: VolunteerOpportunity,
) -> float:
    result = await db.execute(
        select(VolunteerProfile).where(VolunteerProfile.user_id == volunteer_user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return 50.0
    score, _ = compute_match_score(
        volunteer_skills=profile.skills or [],
        volunteer_interests=profile.interests or [],
        volunteer_languages=profile.languages or [],
        opportunity_skills=opportunity.skills_required or [],
        impact_category=opportunity.impact_category,
        is_remote=opportunity.is_remote,
    )
    return score


async def match_opportunities_for_user(
    db: AsyncSession,
    user: User,
    *,
    opportunity_id: uuid.UUID | None = None,
    limit: int = 10,
) -> list[MatchResult]:
    profile = await get_or_create_volunteer_profile(db, user)

    if opportunity_id:
        result = await db.execute(
            select(VolunteerOpportunity).where(
                VolunteerOpportunity.id == opportunity_id,
                VolunteerOpportunity.status == OpportunityStatus.PUBLISHED.value,
            )
        )
        opportunities = [result.scalar_one_or_none()]
        opportunities = [o for o in opportunities if o is not None]
    else:
        result = await db.execute(
            select(VolunteerOpportunity).where(
                VolunteerOpportunity.status == OpportunityStatus.PUBLISHED.value
            )
        )
        opportunities = list(result.scalars().all())

    matches: list[MatchResult] = []
    for opp in opportunities:
        score, reasons = compute_match_score(
            volunteer_skills=profile.skills or [],
            volunteer_interests=profile.interests or [],
            volunteer_languages=profile.languages or [],
            opportunity_skills=opp.skills_required or [],
            impact_category=opp.impact_category,
            is_remote=opp.is_remote,
        )
        matches.append(
            MatchResult(
                opportunity_id=opp.id,
                match_score=score,
                reasons=reasons,
            )
        )

    matches.sort(key=lambda m: m.match_score, reverse=True)
    return matches[:limit]
