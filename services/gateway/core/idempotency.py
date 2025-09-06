
"""
Idempotency key handling utilities for AEC Gateway service
"""

import json
import uuid
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import redis.asyncio as redis

from core.config import settings
from libs.py.aec_shared.errors import ConflictError, create_http_exception
from libs.py.aec_shared.otel import get_current_trace_id

# Redis connection pool
_redis_pool: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    """Get Redis connection"""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_pool

async def close_redis():
    """Close Redis connection"""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None

class IdempotencyKeyManager:
    """Manage idempotency keys for create operations"""
    
    def __init__(self, prefix: str = "idempotency:"):
        self.prefix = prefix
        self.redis = None
    
    async def initialize(self):
        """Initialize Redis connection"""
        self.redis = await get_redis()
    
    async def check_idempotency_key(
        self, 
        key: str, 
        resource_type: str,
        ttl_seconds: int = 3600  # 1 hour default TTL
    ) -> Optional[Dict[str, Any]]:
        """
        Check if idempotency key exists and return stored response if found
        
        Args:
            key: The idempotency key
            resource_type: Type of resource being created (e.g., "project", "rfp")
            ttl_seconds: Time-to-live for the key in seconds
            
        Returns:
            Stored response if key exists, None otherwise
        """
        if not self.redis:
            await self.initialize()
        
        redis_key = f"{self.prefix}{resource_type}:{key}"
        stored_data = await self.redis.get(redis_key)
        
        if stored_data:
            return json.loads(stored_data)
        return None
    
    async def store_idempotency_key(
        self, 
        key: str, 
        resource_type: str,
        response_data: Dict[str, Any],
        ttl_seconds: int = 3600
    ) -> None:
        """
        Store idempotency key with response data
        
        Args:
            key: The idempotency key
            resource_type: Type of resource being created
            response_data: Response data to store
            ttl_seconds: Time-to-live for the key in seconds
        """
        if not self.redis:
            await self.initialize()
        
        redis_key = f"{self.prefix}{resource_type}:{key}"
        await self.redis.setex(
            redis_key, 
            ttl_seconds, 
            json.dumps(response_data)
        )
    
    async def generate_idempotency_key(self) -> str:
        """Generate a new idempotency key"""
        return str(uuid.uuid4())

# Global instance
idempotency_manager = IdempotencyKeyManager()

async def require_idempotency_key(
    idempotency_key: Optional[str] = None,
    resource_type: str = "resource"
) -> str:
    """
    Validate and require idempotency key for create operations
    
    Args:
        idempotency_key: Optional idempotency key from header
        resource_type: Type of resource being created
        
    Returns:
        Valid idempotency key
        
    Raises:
        HTTPException with 400 status if idempotency key is missing
    """
    if not idempotency_key:
        trace_id = get_current_trace_id()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_http_exception(
                status.HTTP_400_BAD_REQUEST,
                "idempotency_key_required",
                "Idempotency-Key header is required for create operations",
                {"resource_type": resource_type},
                trace_id
            ).detail
        )
    return idempotency_key

async def handle_idempotency(
    idempotency_key: str,
    resource_type: str,
    operation: callable,
    *args,
    **kwargs
) -> Any:
    """
    Handle idempotent operation with key checking
    
    Args:
        idempotency_key: The idempotency key
        resource_type: Type of resource being created
        operation: The operation to execute if key is new
        *args, **kwargs: Arguments to pass to the operation
        
    Returns:
        Result of the operation or cached response
        
    Raises:
        ConflictError if operation was already completed with this key
    """
    # Check if we've already processed this request
    cached_response = await idempotency_manager.check_idempotency_key(
        idempotency_key, resource_type
    )
    
    if cached_response:
        trace_id = get_current_trace_id()
        raise ConflictError(
            resource_type, 
            f"already created with idempotency key {idempotency_key}",
            trace_id
        )
    
    # Execute the operation
    result = await operation(*args, **kwargs)
    
    # Store the successful response
    if hasattr(result, 'dict') and callable(getattr(result, 'dict')):
        response_data = result.dict()
    elif isinstance(result, dict):
        response_data = result
    else:
        response_data = {"result": result}
    
    await idempotency_manager.store_idempotency_key(
        idempotency_key, resource_type, response_data
    )
    
    return result
