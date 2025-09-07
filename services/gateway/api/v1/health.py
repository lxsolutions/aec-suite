


"""
Health check endpoints
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from ..dependencies import get_service_health

# Mock functions for testing - these would be implemented with actual checks in production
def check_database_connection() -> bool:
    """Check database connection status"""
    # This would be implemented with actual database connection check
    return True

def check_nats_connection() -> bool:
    """Check NATS connection status"""
    # This would be implemented with actual NATS connection check
    return True

router = APIRouter(prefix="/v1/health", tags=["health"])

# Additional endpoints for Kubernetes health checks
@router.get("/healthz")
async def healthz():
    """Kubernetes health check endpoint"""
    return {"status": "ok"}

@router.get("/readyz")  
async def readyz():
    """Kubernetes readiness check endpoint"""
    services_health = await get_service_health()
    all_healthy = all(service["status"] == "healthy" for service in services_health.values())
    
    if all_healthy:
        return {"status": "ready"}
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "services": services_health}
        )

@router.get("")
async def health_check(detailed: bool = False):
    """Basic health check endpoint"""
    if not detailed:
        return {"status": "healthy", "service": "gateway"}
    
    # For detailed health check, use the mocked functions
    database_connected = check_database_connection()
    nats_connected = check_nats_connection()
    
    # Determine overall status
    all_connected = database_connected and nats_connected
    
    if not all_connected:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy", 
                "service": "gateway",
                "dependencies": {
                    "database": "connected" if database_connected else "disconnected",
                    "nats": "connected" if nats_connected else "disconnected"
                }
            }
        )
    
    return {
        "status": "healthy", 
        "service": "gateway",
        "dependencies": {
            "database": "connected",
            "nats": "connected"
        }
    }

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


