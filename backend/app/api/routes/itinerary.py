from fastapi import APIRouter

router = APIRouter()

@router.get("/itinerary")
async def get_itinerary():
    return {"message": "Itinerary endpoint"}
