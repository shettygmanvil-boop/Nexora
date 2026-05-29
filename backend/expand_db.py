import asyncio
from app.database.core import SessionLocal
from app.models.db_models import Destination

def expand_database():
    with SessionLocal() as session:
        destinations = session.query(Destination).all()
        if not destinations:
            print("No destinations found in DB. Please run setup_db.py first.")
            return

        new_data = {
            "bangalore": {
                "hotels": [
                    {"name": "Taj West End", "tier": "luxury", "price_per_night": 18000, "rating": 4.8, "amenities": ["Heritage Gardens", "Spa", "Fine Dining"], "reviews": ["A colonial era paradise", "Lush green oasis in the city"], "specialty_keyword": "Heritage Luxury"},
                    {"name": "ITC Windsor", "tier": "luxury", "price_per_night": 16000, "rating": 4.7, "amenities": ["Pool", "Irish Pub", "Golf Course View"], "reviews": ["Majestic architecture", "Amazing buffet spread"], "specialty_keyword": "Regal Elegance"},
                    {"name": "Zostel Bangalore", "tier": "budget", "price_per_night": 800, "rating": 4.5, "amenities": ["Bunk Beds", "Common Area", "Wi-Fi"], "reviews": ["Best backpacker vibe", "Great place to meet people"], "specialty_keyword": "Backpacker Friendly"},
                    {"name": "St. Mark's Hotel", "tier": "standard", "price_per_night": 4500, "rating": 4.3, "amenities": ["City View", "Gym", "Breakfast"], "reviews": ["Very central location", "Good corporate stay"], "specialty_keyword": "Central Location"}
                ],
                "attractions": [
                    {"name": "Nandi Hills", "vibe": "scenic", "fatigue_index": 4, "cost": 100, "description": "Beautiful sunrise viewpoint and ancient fortress just outside the city."},
                    {"name": "Bannerghatta Biological Park", "vibe": "nature", "fatigue_index": 3, "cost": 400, "description": "Safari park featuring lions, tigers, and a butterfly conservatory."},
                    {"name": "Commercial Street", "vibe": "shopping", "fatigue_index": 3, "cost": 0, "description": "Bustling street shopping district famous for clothes and accessories."},
                    {"name": "ISKCON Temple", "vibe": "spirituality", "fatigue_index": 2, "cost": 0, "description": "Magnificent hilltop temple offering peace and spiritual serenity."},
                    {"name": "UB City", "vibe": "nightlife", "fatigue_index": 1, "cost": 2000, "description": "Luxury mall featuring high-end restaurants, pubs, and rooftop lounges."}
                ]
            },
            "goa": {
                "hotels": [
                    {"name": "Novotel Goa Resort", "tier": "standard", "price_per_night": 7000, "rating": 4.5, "amenities": ["Swim-up Bar", "Spa", "Kids Club"], "reviews": ["Perfect family resort", "Huge pool area"], "specialty_keyword": "Family Resort"},
                    {"name": "Zostel Goa (Anjuna)", "tier": "budget", "price_per_night": 900, "rating": 4.6, "amenities": ["Café", "Scooter Rental", "Wi-Fi"], "reviews": ["Classic Goan party vibe", "Amazing crowd"], "specialty_keyword": "Party Hostel"},
                    {"name": "Leela Goa", "tier": "luxury", "price_per_night": 22000, "rating": 4.9, "amenities": ["Private Beach", "Golf Course", "Lagoon"], "reviews": ["Absolutely stunning property", "World class luxury"], "specialty_keyword": "Ultra Luxury Resort"}
                ],
                "attractions": [
                    {"name": "Fort Aguada", "vibe": "heritage", "fatigue_index": 3, "cost": 50, "description": "17th-century Portuguese fort standing on Sinquerim Beach overlooking the Arabian Sea."},
                    {"name": "Baga Beach Water Sports", "vibe": "adventure", "fatigue_index": 4, "cost": 1500, "description": "Thrilling parasailing, jet skiing, and banana boat rides."},
                    {"name": "Tito's Lane Nightclub", "vibe": "nightlife", "fatigue_index": 3, "cost": 2000, "description": "The most famous nightclub street in Goa for all-night partying."},
                    {"name": "Dona Paula Viewpoint", "vibe": "scenic", "fatigue_index": 1, "cost": 0, "description": "Romantic viewpoint where two rivers meet the Arabian Sea."}
                ]
            },
            "srinagar": {
                "hotels": [
                    {"name": "Mascot Houseboats", "tier": "standard", "price_per_night": 4500, "rating": 4.6, "amenities": ["Lake View", "Heater", "Traditional Decor"], "reviews": ["Beautiful carved wood interior", "Warm hospitality"], "specialty_keyword": "Premium Houseboat"},
                    {"name": "Four Points by Sheraton", "tier": "luxury", "price_per_night": 12000, "rating": 4.5, "amenities": ["Central Heating", "Fitness Center", "Lounge"], "reviews": ["Modern comfort in the valley", "Reliable and safe"], "specialty_keyword": "Modern Luxury"}
                ],
                "attractions": [
                    {"name": "Pari Mahal", "vibe": "heritage", "fatigue_index": 2, "cost": 50, "description": "Seven terraced gardens overlooking the city of Srinagar and Dal Lake."},
                    {"name": "Shankaracharya Temple", "vibe": "spirituality", "fatigue_index": 3, "cost": 0, "description": "Ancient temple situated on top of the Shankaracharya Hill."},
                    {"name": "Tulip Garden (Seasonal)", "vibe": "nature", "fatigue_index": 2, "cost": 100, "description": "Asia's largest tulip garden bursting with vibrant colors in spring."},
                    {"name": "Floating Vegetable Market", "vibe": "culture", "fatigue_index": 1, "cost": 500, "description": "Early morning vibrant market conducted entirely on wooden boats."}
                ]
            },
            "jaipur": {
                "hotels": [
                    {"name": "Fairmont Jaipur", "tier": "luxury", "price_per_night": 18000, "rating": 4.8, "amenities": ["Aravalli Hills View", "Spa", "Fine Dining"], "reviews": ["Feels like an actual palace", "The welcome ceremony is grand"], "specialty_keyword": "Modern Palace"},
                    {"name": "Zostel Jaipur", "tier": "budget", "price_per_night": 800, "rating": 4.5, "amenities": ["Rooftop Cafe", "Wi-Fi", "Common Room"], "reviews": ["Right near Hawa Mahal", "Great rooftop view"], "specialty_keyword": "Backpacker Vibe"},
                    {"name": "Samode Haveli", "tier": "standard", "price_per_night": 8500, "rating": 4.7, "amenities": ["Courtyard Pool", "Heritage Suites", "Rajasthani Cuisine"], "reviews": ["Authentic Rajputana living", "Beautiful frescoes"], "specialty_keyword": "Authentic Haveli"}
                ],
                "attractions": [
                    {"name": "City Palace", "vibe": "heritage", "fatigue_index": 3, "cost": 300, "description": "A magnificent palace complex showcasing the fusion of Rajput and Mughal architecture."},
                    {"name": "Jantar Mantar", "vibe": "history", "fatigue_index": 2, "cost": 200, "description": "UNESCO World Heritage site featuring giant ancient astronomical instruments."},
                    {"name": "Nahargarh Fort Sunset", "vibe": "scenic", "fatigue_index": 3, "cost": 100, "description": "Spectacular fort offering the best sunset panoramic view of the Pink City."},
                    {"name": "Bapu Bazaar", "vibe": "shopping", "fatigue_index": 4, "cost": 0, "description": "Famous market for traditional Rajasthani textiles, mojari shoes, and handicrafts."}
                ]
            }
        }

        for dest in destinations:
            city_name = dest.name.lower()
            if city_name in new_data:
                # Hotels
                existing_hotel_names = [h.get("name") for h in dest.hotels]
                hotels = list(dest.hotels)
                for h in new_data[city_name]["hotels"]:
                    if h["name"] not in existing_hotel_names:
                        hotels.append(h)
                dest.hotels = hotels

                # Attractions
                existing_attr_names = [a.get("name") for a in dest.attractions]
                attractions = list(dest.attractions)
                for a in new_data[city_name]["attractions"]:
                    if a["name"] not in existing_attr_names:
                        attractions.append(a)
                dest.attractions = attractions
                
        session.commit()
        print("Database successfully expanded with rich, realistic data for all cities!")

if __name__ == "__main__":
    expand_database()
