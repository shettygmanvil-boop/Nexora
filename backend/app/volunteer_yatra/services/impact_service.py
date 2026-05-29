from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.volunteer_yatra.enums import ApplicationStatus, OpportunityStatus
from app.volunteer_yatra.models.application import VolunteerApplication
from app.volunteer_yatra.models.opportunity import VolunteerOpportunity
from app.volunteer_yatra.models.volunteer_profile import VolunteerProfile
from app.volunteer_yatra.schemas.impact import ImpactSummaryResponse


async def get_impact_summary(db: AsyncSession) -> ImpactSummaryResponse:
    hours_result = await db.execute(
        select(func.coalesce(func.sum(VolunteerProfile.volunteer_hours), 0))
    )
    volunteer_hours = float(hours_result.scalar_one())

    active_result = await db.execute(
        select(func.count())
        .select_from(VolunteerOpportunity)
        .where(VolunteerOpportunity.status == OpportunityStatus.PUBLISHED.value)
    )
    active_projects = int(active_result.scalar_one())

    completed_result = await db.execute(
        select(func.count())
        .select_from(VolunteerOpportunity)
        .where(VolunteerOpportunity.status == OpportunityStatus.CLOSED.value)
    )
    completed_projects = int(completed_result.scalar_one())

    volunteers_result = await db.execute(
        select(func.count(func.distinct(VolunteerApplication.volunteer_user_id))).where(
            VolunteerApplication.status == ApplicationStatus.ACCEPTED.value
        )
    )
    active_volunteers = int(volunteers_result.scalar_one())

    opps_result = await db.execute(
        select(VolunteerOpportunity).where(
            VolunteerOpportunity.status == OpportunityStatus.PUBLISHED.value
        )
    )
    opportunities = list(opps_result.scalars().all())

    skill_counter: Counter[str] = Counter()
    location_counter: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()

    for opp in opportunities:
        category_counter[opp.impact_category] += 1
        if opp.location_name:
            location_counter[opp.location_name] += 1
        for skill in opp.skills_required or []:
            skill_counter[skill] += 1

    top_skills = [
        {"skill": k, "count": v} for k, v in skill_counter.most_common(10)
    ]
    top_locations = [
        {"location": k, "count": v} for k, v in location_counter.most_common(10)
    ]
    impact_categories = [
        {"category": k, "count": v} for k, v in category_counter.most_common(10)
    ]

    return ImpactSummaryResponse(
        volunteer_hours=volunteer_hours,
        active_projects=active_projects,
        completed_projects=completed_projects,
        active_volunteers=active_volunteers,
        top_skills=top_skills,
        top_locations=top_locations,
        impact_categories=impact_categories,
    )
