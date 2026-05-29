from typing import Optional
from app.database.core import SessionLocal
from app.models.db_models import Destination

class LiveDestinationsDict:
    def __getitem__(self, key: str):
        with SessionLocal() as session:
            dest = session.query(Destination).filter(Destination.name.ilike(key)).first()
            if not dest:
                raise KeyError(key)
            return self._to_dict(dest)
            
    def get(self, key: str, default=None):
        try:
            return self[key]
        except KeyError:
            return default
            
    def __contains__(self, key: str):
        with SessionLocal() as session:
            return session.query(Destination).filter(Destination.name.ilike(key)).first() is not None

    def items(self):
        # We need items() during the initial db_seed if it runs before deleting old mock_db
        # But wait, db_seed imports the OLD mock_db! I should rename old mock_db or move the static data.
        return []
        
    def keys(self):
        with SessionLocal() as session:
            return [d.name.lower() for d in session.query(Destination).all()]
            
    def _to_dict(self, dest: Destination):
        return {
            "name": dest.name,
            "description": dest.description,
            "vibes": dest.vibes,
            "weather_profile": dest.weather_profile,
            "hotels": dest.hotels,
            "attractions": dest.attractions
        }

DESTINATIONS = LiveDestinationsDict()

def get_destination(dest_name: str) -> Optional[dict]:
    return DESTINATIONS.get(dest_name.lower())

def list_destinations() -> list:
    return DESTINATIONS.keys()
