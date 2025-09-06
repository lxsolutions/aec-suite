

"""
Authentication middleware to extract JWT tokens and set user context
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Optional

from core.security import get_current_user
from libs.py.aec_shared.errors import create_http_exception
from libs.py.aec_shared.otel import get_current_trace_id

class AuthMiddleware:
    """Middleware to authenticate requests and set user context"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        request = Request(scope, receive)
        
        # Skip authentication for public routes
        path = request.url.path
        if any(path.startswith(public_path) for public_path in ["/healthz", "/docs", "/redoc", "/openapi.json"]):
            return await self.app(scope, receive, send)
        
        try:
            # Extract token from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid Authorization header"
                )
            
            token = auth_header.replace("Bearer ", "")
            
            # Get user from token
            user = await get_current_user(token)
            
            # Set user in request state for downstream use
            request.state.user = user
            
        except HTTPException as e:
            # Convert to proper error response
            trace_id = get_current_trace_id()
            response = JSONResponse(
                status_code=e.status_code,
                content=create_http_exception(
                    e.status_code,
                    "unauthorized",
                    str(e.detail),
                    None,
                    trace_id
                ).dict()
            )
            await response(scope, receive, send)
            return
        except Exception as e:
            # Handle other authentication errors
            trace_id = get_current_trace_id()
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=create_http_exception(
                    status.HTTP_401_UNAUTHORIZED,
                    "unauthorized",
                    "Authentication failed",
                    {"error": str(e)},
                    trace_id
                ).dict()
            )
            await response(scope, receive, send)
            return
        
        return await self.app(scope, receive, send)

