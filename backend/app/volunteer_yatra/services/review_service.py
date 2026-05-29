import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.models.user import User
from app.volunteer_yatra.models.host_profile import HostProfile
from app.volunteer_yatra.models.review import VolunteerReview
from app.volunteer_yatra.models.volunteer_profile import VolunteerProfile
from app.volunteer_yatra.schemas.review import ReviewCreate, ReviewSummaryResponse
from app.volunteer_yatra.services.opportunity_service import get_opportunity


async def create_review(
    db: AsyncSession, user: User, data: ReviewCreate
) -> VolunteerReview:
    opp = await get_opportunity(db, data.opportunity_id)
    if user.id not in (opp.host_user_id, data.reviewee_id):
        pass
    if data.reviewer_role == "volunteer" and user.id == opp.host_user_id:
        raise HTTPException(status_code=400, detail="Host cannot review as volunteer")
    if data.reviewer_role == "host" and user.id != opp.host_user_id:
        raise HTTPException(status_code=403, detail="Only host can submit host reviews")

    review = VolunteerReview(
        opportunity_id=data.opportunity_id,
        reviewer_id=user.id,
        reviewee_id=data.reviewee_id,
        reviewer_role=data.reviewer_role,
        rating=data.rating,
        feedback=data.feedback,
    )
    db.add(review)
    await db.flush()
    await _update_reviewee_scores(db, data.reviewee_id, data.reviewer_role)
    await db.refresh(review)
    return review


async def _update_reviewee_scores(
    db: AsyncSession, reviewee_id: uuid.UUID, reviewer_role: str
) -> None:
    avg_result = await db.execute(
        select(func.avg(VolunteerReview.rating), func.count(VolunteerReview.id)).where(
            VolunteerReview.reviewee_id == reviewee_id
        )
    )
    avg_rating, count = avg_result.one()
    avg_rating = float(avg_rating or 0.0)
    count = int(count or 0)

    host_result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == reviewee_id)
    )
    host = host_result.scalar_one_or_none()
    if host:
        host.rating = round(avg_rating, 2)
        host.review_count = count
        host.impact_score = round(avg_rating * 20 + host.impact_score * 0.1, 2)

    vol_result = await db.execute(
        select(VolunteerProfile).where(VolunteerProfile.user_id == reviewee_id)
    )
    vol = vol_result.scalar_one_or_none()
    if vol:
        vol.impact_score = round(avg_rating * 20 + vol.impact_score * 0.1, 2)

    await db.flush()


async def get_review_summary(
    db: AsyncSession, user_id: uuid.UUID
) -> ReviewSummaryResponse:
    avg_result = await db.execute(
        select(func.avg(VolunteerReview.rating), func.count(VolunteerReview.id)).where(
            VolunteerReview.reviewee_id == user_id
        )
    )
    avg_rating, count = avg_result.one()

    impact = 0.0
    vol_result = await db.execute(
        select(VolunteerProfile).where(VolunteerProfile.user_id == user_id)
    )
    vol = vol_result.scalar_one_or_none()
    if vol:
        impact = vol.impact_score
    else:
        host_result = await db.execute(
            select(HostProfile).where(HostProfile.user_id == user_id)
        )
        host = host_result.scalar_one_or_none()
        if host:
            impact = host.impact_score

    return ReviewSummaryResponse(
        user_id=user_id,
        average_rating=round(float(avg_rating or 0.0), 2),
        review_count=int(count or 0),
        impact_score=impact,
    )
