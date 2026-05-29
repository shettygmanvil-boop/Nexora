from sqlalchemy import Column, String, JSON, Integer
from app.database.core import Base

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    
    # Store lists and dicts natively in PostgreSQL JSON
    vibes = Column(JSON, nullable=False)
    weather_profile = Column(JSON, nullable=False)
    hotels = Column(JSON, nullable=False)
    attractions = Column(JSON, nullable=False)
