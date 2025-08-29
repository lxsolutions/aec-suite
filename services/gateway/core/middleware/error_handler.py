
"""
Error handling middleware for uniform error responses
"""

import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette import status

from libs.py.aec_shared.errors import AECError
from libs.py.aec_shared.otel import get_current_trace_id

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as http_exc:
            # Handle FastAPI HTTP exceptions
            trace_id = get_current_trace_id()
            error_response = AECError(
                traceId=trace_id,
                code=http_exc.status_code,
                message=http_exc.detail,
                details=getattr(http_exc, "details", None)
            )
            return JSONResponse(
                status_code=http_exc.status_code,
                content=error_response.dict(exclude_none=True)
            )
            
        except Exception as exc:
            # Handle unexpected exceptions
            trace_id = get_current_trace_id()
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            
            error_response = AECError(
                traceId=trace_id,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Internal server error",
                details={"exception_type": type(exc).__name__}
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response.dict(exclude_none=True)
            )

def create_error_handler_middleware():
    """Create error handler middleware"""
    return ErrorHandlerMiddleware

