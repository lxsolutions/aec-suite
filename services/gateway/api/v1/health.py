


"""
Health check endpoints
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from ..dependencies import get_service_health

router = APIRouter(prefix="/v1/health", tags=["health"])

@router.get("")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "gateway"}

@router.get("/ready")
async def readiness_check():
    """Readiness check including dependencies"""
    services_health = await get_service_health()
    
    all_healthy = all(service["status"] == "healthy" for service in services_health.values())
    
    if all_healthy:
        return {
            "status": "ready", 
            "services": services_health
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "services": services_health
            }
        )


