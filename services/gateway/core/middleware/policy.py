
"""
Policy middleware for role-based access control and tenant isolation
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Dict, Any, Optional
import re

from libs.py.aec_shared.models import UserRole
from libs.py.aec_shared.errors import create_http_exception
from libs.py.aec_shared.otel import get_current_trace_id

# Route policy definitions - maps route patterns to required roles
ROUTE_POLICIES = [
    # Admin routes - full organization access
    (r"^/v1/admin/.*", [UserRole.ORG_ADMIN]),
    
    # Project management routes
    (r"^/v1/projects$", [UserRole.PROJECT_MANAGER, UserRole.ORG_ADMIN]),  # Create projects
    (r"^/v1/projects/.*", [UserRole.PROJECT_MANAGER, UserRole.ESTIMATOR, UserRole.ORG_ADMIN]),  # Manage projects
    
    # Estimate routes
    (r"^/v1/estimates$", [UserRole.ESTIMATOR, UserRole.PROJECT_MANAGER, UserRole.ORG_ADMIN]),  # Create estimates
    (r"^/v1/estimates/.*", [UserRole.ESTIMATOR, UserRole.PROJECT_MANAGER, UserRole.ORG_ADMIN, UserRole.VIEWER]),  # View/manage estimates
    
    # RFP routes  
    (r"^/v1/rfps.*", [UserRole.PROJECT_MANAGER, UserRole.ESTIMATOR, UserRole.ORG_ADMIN, UserRole.VIEWER]),
    
    # Health and public routes (no auth required)
    (r"^/healthz$", []),
    (r"^/docs$", []),
    (r"^/redoc$", []),
    (r"^/openapi.json$", []),
]

class PolicyMiddleware:
    """Middleware for role-based access control"""
    
    def __init__(self, app):
        self.app = app
        self.compiled_policies = [
            (re.compile(pattern), roles) for pattern, roles in ROUTE_POLICIES
        ]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        request = Request(scope, receive)
        path = request.url.path
        
        # Find matching policy for the route
        required_roles = None
        for pattern, roles in self.compiled_policies:
            if pattern.match(path):
                required_roles = roles
                break
        
        # If no policy matches, require authentication by default
        if required_roles is None:
            required_roles = [UserRole.ORG_ADMIN, UserRole.PROJECT_MANAGER, UserRole.ESTIMATOR, UserRole.VIEWER]
        
        # Public routes don't require authentication
        if not required_roles:
            return await self.app(scope, receive, send)
        
        # Check if user is authenticated and has required roles
        try:
            # Get user from request state (set by authentication middleware)
            user = request.state.user
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user has any of the required roles
            if not any(role in user.roles for role in required_roles):
                trace_id = get_current_trace_id()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=create_http_exception(
                        status.HTTP_403_FORBIDDEN,
                        "forbidden",
                        "Insufficient permissions for this resource",
                        {"required_roles": [r.value for r in required_roles]},
                        trace_id
                    ).detail
                )
                
        except HTTPException as e:
            # Convert HTTPException to proper response
            if scope["type"] == "http":
                response = JSONResponse(
                    status_code=e.status_code,
                    content=e.detail if isinstance(e.detail, dict) else {"detail": str(e.detail)}
                )
                await response(scope, receive, send)
                return
            else:
                raise e
        except Exception:
            # If no user in request state, require authentication
            trace_id = get_current_trace_id()
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=create_http_exception(
                    status.HTTP_401_UNAUTHORIZED,
                    "unauthorized",
                    "Authentication required",
                    None,
                    trace_id
                ).dict()
            )
            await response(scope, receive, send)
            return
        
        return await self.app(scope, receive, send)

def get_required_roles(path: str) -> Optional[list]:
    """Get required roles for a specific path"""
    for pattern, roles in ROUTE_POLICIES:
        if re.compile(pattern).match(path):
            return roles
    return None
