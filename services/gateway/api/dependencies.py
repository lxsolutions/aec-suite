
"""
API dependencies and utilities
"""

import httpx
from fastapi import HTTPException, status, Header
from typing import Dict, Any, Optional

from core.config import settings
from libs.py.aec_shared.errors import ServiceUnavailableError, create_http_exception
from libs.py.aec_shared.otel import get_current_trace_id

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
    trace_id = get_current_trace_id()
    async with httpx.AsyncClient() as client:
        try:
            method_fn = getattr(client, method.lower())
            response = await method_fn(service_url, **kwargs, timeout=30.0)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            # Forward the upstream service error with proper formatting
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "code" in error_data and "message" in error_data:
                    # This is already a standardized error from upstream service
                    raise HTTPException(
                        status_code=e.response.status_code,
                        detail=create_http_exception(
                            e.response.status_code,
                            error_data.get("code", "service_error"),
                            error_data.get("message", "Service error"),
                            error_data.get("details"),
                            trace_id
                        ).detail
                    )
            except (ValueError, TypeError):
                # Fallback for non-JSON responses or malformed errors
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=create_http_exception(
                        e.response.status_code,
                        "service_error",
                        f"Service error: {e.response.text}",
                        None,
                        trace_id
                    ).detail
                )
        except httpx.RequestError as e:
            raise ServiceUnavailableError("orchestrator", trace_id)

async def get_org_id() -> str:
    """Get organization ID from context (stub for now)"""
    # TODO: Implement proper JWT auth extraction
    return "org-123"

async def get_idempotency_key(idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")) -> Optional[str]:
    """Get idempotency key from header"""
    return idempotency_key
