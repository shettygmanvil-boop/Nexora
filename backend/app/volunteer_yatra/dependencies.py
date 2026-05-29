"""FastAPI dependencies for Volunteer Yatra (auth stub until platform auth ships)."""

import uuid

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db
from app.platform.models.user import User


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    x_dev_user_id: str | None = Header(None, alias="X-Dev-User-Id"),
    x_dev_user_email: str | None = Header(None, alias="X-Dev-User-Email"),
) -> User:
    """
    Development auth: pass X-Dev-User-Id (UUID) to identify the caller.
    Auto-provisions a user record when the ID is new.
    """
    if not settings.volunteer_yatra_enabled:
        raise HTTPException(status_code=503, detail="Volunteer Yatra module is disabled")

    if not x_dev_user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Provide X-Dev-User-Id header (dev mode).",
        )

    try:
        user_id = uuid.UUID(x_dev_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid X-Dev-User-Id") from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        email = x_dev_user_email or f"dev-{user_id}@mapwork.local"
        user = User(
            id=user_id,
            email=email,
            display_name=f"User {str(user_id)[:8]}",
        )
        db.add(user)
        await db.flush()

    return user


async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    x_dev_user_id: str | None = Header(None, alias="X-Dev-User-Id"),
) -> User | None:
    if not x_dev_user_id:
        return None
    try:
        user_id = uuid.UUID(x_dev_user_id)
    except ValueError:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
