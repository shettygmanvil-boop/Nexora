from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

# Create the async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Create the async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for declarative models
Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Sync engine for background tasks/services that are currently synchronous
sync_engine = create_engine(
    settings.database_url.replace("+aiosqlite", ""),
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async db sessions."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
