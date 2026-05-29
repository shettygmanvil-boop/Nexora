from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.volunteer_yatra.schemas.impact import ImpactSummaryResponse
from app.volunteer_yatra.services import impact_service

router = APIRouter(prefix="/impact", tags=["Volunteer Impact"])


@router.get("/summary", response_model=ImpactSummaryResponse)
async def get_impact_summary(db: AsyncSession = Depends(get_db)):
    return await impact_service.get_impact_summary(db)
