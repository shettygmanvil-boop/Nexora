import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.core import engine, Base
from app.models.db_models import Destination
from app.database.static_data import DESTINATIONS

logger = logging.getLogger(__name__)

async def initialize_database():
    """Create tables and seed the database with mock destinations if empty."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed data
    from app.database.core import async_session
    async with async_session() as session:
        try:
            # Check if we already have destinations
            result = await session.execute(select(Destination))
            existing_dests = result.scalars().all()
            
            if not existing_dests:
                logger.info("Database is empty. Seeding with mock destinations...")
                for dest_key, dest_data in DESTINATIONS.items():
                    new_dest = Destination(
                        name=dest_data["name"],
                        description=dest_data["description"],
                        vibes=dest_data["vibes"],
                        weather_profile=dest_data["weather_profile"],
                        hotels=dest_data.get("hotels", []),
                        attractions=dest_data.get("attractions", [])
                    )
                    session.add(new_dest)
                
                await session.commit()
                logger.info("Successfully seeded mock destinations into the database.")
            else:
                logger.info(f"Database already contains {len(existing_dests)} destinations. Skipping seed.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding database: {e}")
