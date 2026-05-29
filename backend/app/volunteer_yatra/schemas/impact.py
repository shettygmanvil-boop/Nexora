from pydantic import BaseModel


class ImpactSummaryResponse(BaseModel):
    volunteer_hours: float
    active_projects: int
    completed_projects: int
    active_volunteers: int
    top_skills: list[dict]
    top_locations: list[dict]
    impact_categories: list[dict]
