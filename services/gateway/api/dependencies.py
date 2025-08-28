
"""
API dependencies and utilities
"""

import httpx
from fastapi import HTTPException, status
from typing import Dict, Any

from ..core.config import settings

async def get_service_health() -> Dict[str, Dict[str, Any]]:
    """Check health of all backend services"""
    services = {
        "orchestrator": settings.ORCHESTRATOR_URL + "/healthz",
        "rover": settings.ROVER_URL + "/healthz",
        "erp_bridge": settings.ERP_BRIDGE_URL + "/healthz",
        "buildforge": settings.BUILDFORGE_URL + "/healthz",
    }
    
    health_status = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, health_url in services.items():
            try:
                response = await client.get(health_url, timeout=2.0)
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }
    
    return health_status

async def call_service(service_url: str, method: str = "get", **kwargs) -> httpx.Response:
    """Make HTTP call to backend service"""
    async with httpx.AsyncClient() as client:
        try:
            method_fn = getattr(client, method.lower())
            response = await method_fn(service_url, **kwargs, timeout=30.0)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Service error: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service unavailable: {str(e)}"
            )

async def get_org_id() -> str:
    """Get organization ID from context (stub for now)"""
    # TODO: Implement proper JWT auth extraction
    return "org-123"
