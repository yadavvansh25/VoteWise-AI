"""
VoteWise AI — Health Check Endpoint
"""

from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint for monitoring."""
    settings = get_settings()

    services = {
        "api": "healthy",
        "gemini": "configured" if settings.GEMINI_API_KEY else "not_configured",
        "cache": "healthy",
    }

    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        services=services,
    )
