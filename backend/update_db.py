import asyncio
from app.database.core import SessionLocal
from app.models.db_models import Destination

def update_bangalore():
    with SessionLocal() as session:
        dest = session.query(Destination).filter(Destination.name.ilike('bangalore')).first()
        if dest:
            # We need to copy the list to mutate it and re-assign so SQLAlchemy detects the change
            attractions = list(dest.attractions)
            
            new_places = [
                {"name": "Wonderla Amusement Park", "vibe": "adventure", "fatigue_index": 5, "cost": 1500, "description": "High-thrill amusement park with water rides and rollercoasters."},
                {"name": "Innovative Film City", "vibe": "entertainment", "fatigue_index": 4, "cost": 1000, "description": "Movie theme park with reality TV sets, museums, and rides."},
                {"name": "Fun World Amusement Park", "vibe": "adventure", "fatigue_index": 4, "cost": 800, "description": "Classic amusement park with family rides and a snow city."}
            ]
            
            # Check if they already exist to avoid duplicates
            existing_names = [a.get("name") for a in attractions]
            for p in new_places:
                if p["name"] not in existing_names:
                    attractions.append(p)
                    
            dest.attractions = attractions
            session.commit()
            print("Successfully added Wonderla, Innovative Film City, and Fun World to Bangalore in the database!")
        else:
            print("Bangalore destination not found in db.")

if __name__ == "__main__":
    update_bangalore()
