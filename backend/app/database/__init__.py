"""
Database Module - Maproom Backend

This package handles database connections and mock database stores.
For the Maproom hackathon project, it contains a curated repository of travel destination details,
hotels, attractions, and weather profiles to support simulated travel orchestration.
"""

from app.database.destinations import (
    get_all_destinations,
    get_destination_by_name,
    get_destinations_by_vibe
)

