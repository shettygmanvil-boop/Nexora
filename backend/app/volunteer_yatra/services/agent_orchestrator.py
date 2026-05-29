"""Volunteer Yatra AI agents — isolated from travel crew_service."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.platform.models.user import User
from app.volunteer_yatra.schemas.agent import (
    ImpactNarrativeResponse,
    MatchResponse,
    RecommendationResponse,
    SafetyCheckResponse,
)
from app.volunteer_yatra.services.impact_service import get_impact_summary
from app.volunteer_yatra.services.matching_service import match_opportunities_for_user
from app.volunteer_yatra.services.opportunity_service import get_opportunity

logger = logging.getLogger(__name__)


async def run_matching(
    db: AsyncSession,
    user: User,
    *,
    opportunity_id: uuid.UUID | None = None,
    limit: int = 10,
) -> MatchResponse:
    matches = await match_opportunities_for_user(
        db, user, opportunity_id=opportunity_id, limit=limit
    )
    return MatchResponse(matches=matches)


async def run_recommendations(
    db: AsyncSession,
    user: User,
    limit: int = 10,
) -> RecommendationResponse:
    match_response = await run_matching(db, user, limit=limit)
    ids = [m.opportunity_id for m in match_response.matches]
    summaries = [
        f"Match score {m.match_score}%: {'; '.join(m.reasons[:2])}"
        for m in match_response.matches
    ]
    return RecommendationResponse(opportunity_ids=ids, summaries=summaries)


async def run_safety_check(
    db: AsyncSession,
    *,
    opportunity_id: uuid.UUID | None = None,
    title: str | None = None,
    description: str | None = None,
) -> SafetyCheckResponse:
    flags: list[str] = []
    risk_level = "low"

    if opportunity_id:
        opp = await get_opportunity(db, opportunity_id)
        title = opp.title
        description = opp.description

    text = f"{title or ''} {description or ''}".lower()

    risky_terms = ["wire transfer", "pay upfront", "no contract", "whatsapp only"]
    for term in risky_terms:
        if term in text:
            flags.append(f"Contains risky phrase: '{term}'")
            risk_level = "high"

    if description and len(description) < 30:
        flags.append("Description is very short")
        risk_level = "medium" if risk_level == "low" else risk_level

    if not title:
        flags.append("Missing title")
        risk_level = "medium"

    moderation = "approve"
    if risk_level == "high":
        moderation = "manual_review"
    elif risk_level == "medium":
        moderation = "review_recommended"

    if settings.openai_api_key and description:
        try:
            llm_result = await _llm_safety_check(title or "", description)
            if llm_result:
                return llm_result
        except Exception as exc:
            logger.warning("Safety LLM fallback: %s", exc)

    return SafetyCheckResponse(
        risk_level=risk_level,
        flags=flags or ["No issues detected by rule engine"],
        moderation_recommendation=moderation,
    )


async def _llm_safety_check(title: str, description: str) -> SafetyCheckResponse | None:
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage

        llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )
        prompt = (
            "Analyze this volunteer opportunity for safety risks. "
            "Reply with JSON only: {\"risk_level\": \"low|medium|high\", "
            "\"flags\": [\"...\"], \"moderation_recommendation\": \"approve|review_recommended|manual_review\"}\n\n"
            f"Title: {title}\nDescription: {description}"
        )
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        import json
        import re

        content = str(response.content)
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return SafetyCheckResponse(**data)
    except Exception:
        return None
    return None


async def run_impact_narrative(db: AsyncSession) -> ImpactNarrativeResponse:
    summary = await get_impact_summary(db)
    highlights = [
        f"{summary.volunteer_hours:.0f} total volunteer hours logged",
        f"{summary.active_projects} active projects",
        f"{summary.completed_projects} completed projects",
        f"{summary.active_volunteers} active volunteers",
    ]
    if summary.top_skills:
        top = summary.top_skills[0]
        highlights.append(f"Top skill in demand: {top['skill']}")
    narrative = (
        f"Community impact snapshot: {summary.active_volunteers} volunteers contributing "
        f"across {summary.active_projects} active projects with "
        f"{summary.volunteer_hours:.0f} hours of service recorded."
    )
    return ImpactNarrativeResponse(summary=narrative, highlights=highlights)
