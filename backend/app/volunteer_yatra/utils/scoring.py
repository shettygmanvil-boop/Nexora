"""Rule-based volunteer–opportunity matching (LLM fallback)."""

from __future__ import annotations


def compute_match_score(
    volunteer_skills: list[str],
    volunteer_interests: list[str],
    volunteer_languages: list[str],
    opportunity_skills: list[str],
    impact_category: str,
    is_remote: bool,
    prefers_remote: bool | None = None,
) -> tuple[float, list[str]]:
    """
    Returns (score 0-100, reasons).
    """
    reasons: list[str] = []
    score = 40.0

    vol_skills = {s.lower().strip() for s in volunteer_skills if s}
    opp_skills = {s.lower().strip() for s in opportunity_skills if s}

    if opp_skills:
        overlap = vol_skills & opp_skills
        if overlap:
            ratio = len(overlap) / len(opp_skills)
            skill_pts = min(40.0, ratio * 40.0)
            score += skill_pts
            reasons.append(f"Skill overlap: {', '.join(sorted(overlap))}")
        else:
            reasons.append("No direct skill overlap — consider building related skills")
    else:
        score += 15.0
        reasons.append("Opportunity has flexible skill requirements")

    vol_interests = {i.lower().strip() for i in volunteer_interests if i}
    if impact_category.lower() in vol_interests:
        score += 15.0
        reasons.append(f"Interest aligns with impact category: {impact_category}")

    if prefers_remote is not None:
        if prefers_remote == is_remote:
            score += 10.0
            reasons.append("Location preference matches (remote/onsite)")
        else:
            score -= 5.0
            reasons.append("Location preference may not match")

    if volunteer_languages:
        score += 5.0
        reasons.append("Multilingual volunteer profile")

    score = max(0.0, min(100.0, round(score, 1)))
    if not reasons:
        reasons.append("Baseline compatibility from profile data")
    return score, reasons
