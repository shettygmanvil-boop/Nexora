from fastapi import APIRouter

from app.volunteer_yatra.routes import (
    agents,
    applications,
    impact,
    opportunities,
    profiles,
    reviews,
    tasks,
    verification,
)

router = APIRouter()

router.include_router(opportunities.router)
router.include_router(applications.router)
router.include_router(profiles.router)
router.include_router(tasks.router)
router.include_router(reviews.router)
router.include_router(verification.router)
router.include_router(impact.router)
router.include_router(agents.router)
