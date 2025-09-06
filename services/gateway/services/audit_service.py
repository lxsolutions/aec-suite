



"""
Audit logging service for tracking user actions and access patterns
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.audit_log import AuditLog
from db import get_db
from libs.py.aec_shared.otel import get_current_trace_id

logger = logging.getLogger(__name__)

class AuditService:
    """Service for recording audit logs"""
    
    @staticmethod
    async def log_action(
        request: Request,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        db_session: Optional[AsyncSession] = None
    ) -> None:
        """Log an audit action"""
        try:
            # Get user context from request
            user = getattr(request.state, 'user', None)
            if not user:
                logger.warning("No user context available for audit logging")
                return
            
            # Create audit log entry
            audit_log = AuditLog(
                org_id=user.org_id,
                user_id=user.user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                trace_id=get_current_trace_id()
            )
            
            # Use provided session or create new one
            if db_session:
                db_session.add(audit_log)
                await db_session.commit()
            else:
                async with get_db(request) as session:
                    session.add(audit_log)
                    await session.commit()
                    
            logger.info(f"Audit log recorded: {action} on {resource_type} {resource_id or ''}")
            
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")
            # Don't raise exception as audit logging shouldn't break the main flow

    @staticmethod
    async def log_access(
        request: Request,
        resource_type: str,
        resource_id: Optional[str] = None,
        action: str = "access"
    ) -> None:
        """Log resource access"""
        await AuditService.log_action(
            request, action, resource_type, resource_id, {"method": request.method}
        )

    @staticmethod
    async def log_create(
        request: Request,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log resource creation"""
        await AuditService.log_action(
            request, "create", resource_type, resource_id, details
        )

    @staticmethod
    async def log_update(
        request: Request,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log resource update"""
        await AuditService.log_action(
            request, "update", resource_type, resource_id, details
        )

    @staticmethod
    async def log_delete(
        request: Request,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log resource deletion"""
        await AuditService.log_action(
            request, "delete", resource_type, resource_id, details
        )

    @staticmethod
    async def log_permission_denied(
        request: Request,
        resource_type: str,
        resource_id: Optional[str] = None,
        reason: str = "insufficient_permissions"
    ) -> None:
        """Log permission denied events"""
        await AuditService.log_action(
            request, "permission_denied", resource_type, resource_id, {"reason": reason}
        )


# FastAPI dependency for easy access
async def get_audit_service() -> AuditService:
    """Dependency to get audit service instance"""
    return AuditService()


