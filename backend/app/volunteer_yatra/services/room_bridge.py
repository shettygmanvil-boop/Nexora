"""Creates platform rooms for volunteer opportunities."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.models.room import Room
from app.volunteer_yatra.models.opportunity import VolunteerOpportunity


async def create_volunteer_room(
    db: AsyncSession,
    opportunity: VolunteerOpportunity,
    host_user_id: uuid.UUID,
) -> Room:
    room = Room(
        name=f"Volunteer: {opportunity.title[:200]}",
        room_type="volunteer",
        created_by_id=host_user_id,
        metadata_={
            "opportunity_id": str(opportunity.id),
            "impact_category": opportunity.impact_category,
        },
    )
    db.add(room)
    await db.flush()
    opportunity.room_id = room.id
    return room
