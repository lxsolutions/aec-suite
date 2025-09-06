



"""
Audit logging middleware for automatic access logging
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable, Optional
import re

from services.audit_service import AuditService

# Routes that should be audited (exclude health checks, docs, etc.)
AUDIT_ROUTE_PATTERNS = [
    r"^/v1/projects.*",
    r"^/v1/rfps.*", 
    r"^/v1/estimates.*",
    r"^/v1/admin.*"
]

# Routes to exclude from auditing
EXCLUDE_ROUTE_PATTERNS = [
    r"^/healthz.*",
    r"^/docs.*",
    r"^/redoc.*",
    r"^/openapi\.json.*"
]

class AuditLoggerMiddleware:
    """Middleware for automatic audit logging of API access"""
    
    def __init__(self, app):
        self.app = app
        self.audit_patterns = [re.compile(pattern) for pattern in AUDIT_ROUTE_PATTERNS]
        self.exclude_patterns = [re.compile(pattern) for pattern in EXCLUDE_ROUTE_PATTERNS]
    
    def should_audit(self, path: str) -> bool:
        """Determine if a route should be audited"""
        # Check if path matches any exclude patterns
        if any(pattern.match(path) for pattern in self.exclude_patterns):
            return False
        
        # Check if path matches any audit patterns
        return any(pattern.match(path) for pattern in self.audit_patterns)
    
    def extract_resource_info(self, path: str, method: str) -> tuple:
        """Extract resource type and ID from path"""
        # Map paths to resource types
        resource_map = {
            r"^/v1/projects.*": "project",
            r"^/v1/rfps.*": "rfp",
            r"^/v1/estimates.*": "estimate",
            r"^/v1/admin.*": "admin"
        }
        
        # Determine resource type
        resource_type = "unknown"
        for pattern, res_type in resource_map.items():
            if re.compile(pattern).match(path):
                resource_type = res_type
                break
        
        # Extract resource ID from path (e.g., /v1/projects/123 -> 123)
        resource_id = None
        if resource_type != "unknown":
            id_match = re.search(r'/([a-f0-9-]{36}|[0-9]+)(/|$)', path)
            if id_match:
                resource_id = id_match.group(1)
        
        # Determine action based on HTTP method
        action_map = {
            "GET": "access",
            "POST": "create", 
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete"
        }
        action = action_map.get(method, "access")
        
        return resource_type, resource_id, action
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        request = Request(scope, receive)
        path = request.url.path
        method = request.method
        
        # Only audit specific routes
        if not self.should_audit(path):
            return await self.app(scope, receive, send)
        
        try:
            # Extract resource information
            resource_type, resource_id, action = self.extract_resource_info(path, method)
            
            # Log the access
            await AuditService.log_access(
                request,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action
            )
            
        except Exception as e:
            # Don't break the request if audit logging fails
            pass
        
        return await self.app(scope, receive, send)


