from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["Diagnostics"])

@router.get("/health")
def health_check():
    """
    Standard health check endpoint to verify backend status.
    """
    return {
        "status": "healthy",
        "service": "Maproom AI Travel Engine",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }
