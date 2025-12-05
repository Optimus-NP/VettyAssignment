"""
Health check router.

Provides endpoints for health checks and version information.
"""

from fastapi import APIRouter

from app.config import settings
from app.models import HealthCheck
from app.services import coingecko_service

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    response_model=HealthCheck,
    summary="Health check",
    description="Check the health status of the API and external services"
)
async def health_check() -> HealthCheck:
    """
    Check the health status of the API and CoinGecko service.
    
    This endpoint does not require authentication and can be used
    for monitoring and load balancer health checks.
    
    Returns:
        HealthCheck object with status information
    """
    # Check CoinGecko API availability
    coingecko_healthy = coingecko_service.check_health()
    coingecko_status = "healthy" if coingecko_healthy else "unhealthy"
    
    return HealthCheck(
        status="healthy",
        version=settings.api_version,
        coingecko_status=coingecko_status
    )


@router.get(
    "/version",
    summary="Get API version",
    description="Get the current version of the API"
)
async def get_version() -> dict:
    """
    Get the current API version.
    
    This endpoint does not require authentication.
    
    Returns:
        Dictionary with version information
    """
    return {
        "version": settings.api_version,
        "title": settings.api_title
    }
