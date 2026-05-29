import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Float, Integer, String, Uuid, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.volunteer_yatra.enums import VerificationStatus


class VolunteerProfile(Base):
    __tablename__ = "volunteer_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    skills: Mapped[list] = mapped_column(JSON, default=list)
    languages: Mapped[list] = mapped_column(JSON, default=list)
    availability: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    interests: Mapped[list] = mapped_column(JSON, default=list)
    portfolio_links: Mapped[list] = mapped_column(JSON, default=list)
    volunteer_hours: Mapped[float] = mapped_column(Float, default=0.0)
    completed_projects: Mapped[int] = mapped_column(Integer, default=0)
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)
    verification_status: Mapped[str] = mapped_column(
        String(32), default=VerificationStatus.PENDING.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="volunteer_profile")
