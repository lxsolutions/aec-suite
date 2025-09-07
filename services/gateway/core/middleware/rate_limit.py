

"""
Rate limiting middleware for AEC Gateway
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, HTTPException, status
from typing import Callable, Optional

from core.config import settings

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT] if settings.RATE_LIMIT_ENABLED else []
)

def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key based on request path and authentication status"""
    key = get_remote_address(request)
    
    # Differentiate by endpoint type
    path = request.url.path
    if path.startswith("/v1/rfps/ingest") or path.startswith("/v1/rfps/upload"):
        return f"{key}:upload"
    elif path.startswith("/v1/"):
        # Check if user is authenticated (simplified)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return f"{key}:authenticated"
    
    return key

def create_rate_limit_middleware() -> Optional[Callable]:
    """Create rate limiting middleware if enabled"""
    if not settings.RATE_LIMIT_ENABLED:
        return None
    
    # Configure specific limits
    limiter.limit(settings.RATE_LIMIT_UPLOADS, key_func=lambda request: f"{get_remote_address(request)}:upload")
    limiter.limit(settings.RATE_LIMIT_AUTHENTICATED, key_func=lambda request: f"{get_remote_address(request)}:authenticated")
    
    return SlowAPIMiddleware

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors"""
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": f"{exc.retry_after} seconds",
            "limit": exc.detail.limit,
            "remaining": 0
        },
        headers={"Retry-After": str(exc.retry_after)}
    )

# Export the limiter for use in specific endpoints
__all__ = ["limiter", "create_rate_limit_middleware", "rate_limit_exceeded_handler"]

