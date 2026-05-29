import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.volunteer_yatra.enums import OpportunityStatus


class VolunteerOpportunity(Base):
    __tablename__ = "volunteer_opportunities"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    host_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    room_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    skills_required: Mapped[list] = mapped_column(JSON, default=list)
    duration: Mapped[str] = mapped_column(String(64), default="flexible")
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    food_included: Mapped[bool] = mapped_column(Boolean, default=False)
    accommodation_included: Mapped[bool] = mapped_column(Boolean, default=False)
    impact_category: Mapped[str] = mapped_column(String(64), index=True)
    capacity: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(
        String(32), default=OpportunityStatus.DRAFT.value, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    applications = relationship(
        "VolunteerApplication",
        back_populates="opportunity",
        cascade="all, delete-orphan",
    )
    tasks = relationship(
        "VolunteerTask",
        back_populates="opportunity",
        cascade="all, delete-orphan",
    )
