

"""
Uniform error handling for AEC Suite
"""

from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from pydantic import BaseModel


class AECError(BaseModel):
    """Uniform error response format"""
    trace_id: Optional[str] = None
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "code": "validation_error",
                "message": "Invalid input data",
                "details": {"field": "email", "issue": "invalid_format"}
            }
        }


def create_http_exception(
    status_code: int,
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None
) -> HTTPException:
    """Create a standardized HTTP exception"""
    error = AECError(
        trace_id=trace_id,
        code=code,
        message=message,
        details=details
    )
    return HTTPException(status_code=status_code, detail=error.dict())


# Common error types
class ValidationError(HTTPException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, trace_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_http_exception(
                status.HTTP_400_BAD_REQUEST,
                "validation_error",
                message,
                details,
                trace_id
            ).detail
        )


class NotFoundError(HTTPException):
    def __init__(self, resource_type: str, resource_id: str, trace_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_http_exception(
                status.HTTP_404_NOT_FOUND,
                "not_found",
                f"{resource_type} with id {resource_id} not found",
                {"resource_type": resource_type, "resource_id": resource_id},
                trace_id
            ).detail
        )


class UnauthorizedError(HTTPException):
    def __init__(self, message: str = "Unauthorized", trace_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_http_exception(
                status.HTTP_401_UNAUTHORIZED,
                "unauthorized",
                message,
                None,
                trace_id
            ).detail
        )


class ForbiddenError(HTTPException):
    def __init__(self, message: str = "Forbidden", trace_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=create_http_exception(
                status.HTTP_403_FORBIDDEN,
                "forbidden",
                message,
                None,
                trace_id
            ).detail
        )


class InternalServerError(HTTPException):
    def __init__(self, message: str = "Internal server error", trace_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_http_exception(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "internal_error",
                message,
                None,
                trace_id
            ).detail
        )


class ServiceUnavailableError(HTTPException):
    def __init__(self, service_name: str, trace_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=create_http_exception(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "service_unavailable",
                f"{service_name} service is unavailable",
                {"service": service_name},
                trace_id
            ).detail
        )

