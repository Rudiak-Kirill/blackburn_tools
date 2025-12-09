"""
Health check endpoint
"""
from fastapi import APIRouter
from app.schemas import HealthResponse
from app.core.config import settings
from app import __version__

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        version=__version__,
        environment=settings.APP_ENV
    )
