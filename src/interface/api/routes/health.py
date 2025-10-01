"""Health check routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "areamedica-api"}


@router.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # TODO: Add database and external services checks
    return {"status": "ready", "service": "areamedica-api"}
