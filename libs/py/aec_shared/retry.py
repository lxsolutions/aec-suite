

"""
Retry utilities with exponential backoff and dead-letter queue support
for NATS consumers and other distributed systems
"""

import asyncio
import logging
import time
from typing import Callable, Optional, Dict, Any
from functools import wraps
import json

logger = logging.getLogger(__name__)

class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_retries: int = 5,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

class DeadLetterQueue:
    """Dead letter queue for messages that cannot be processed"""
    
    def __init__(self, nats_client=None, dlq_subject: str = "dlq.messages"):
        self.nats_client = nats_client
        self.dlq_subject = dlq_subject
    
    async def send_to_dlq(self, message_data: Dict[str, Any], error: Exception, context: Dict[str, Any] = None):
        """Send message to dead letter queue"""
        if not self.nats_client:
            logger.warning("No NATS client configured for DLQ")
            return
        
        dlq_message = {
            "original_message": message_data,
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": time.time(),
            "context": context or {}
        }
        
        try:
            await self.nats_client.publish(self.dlq_subject, dlq_message)
            logger.info(f"Message sent to DLQ: {dlq_message}")
        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {e}")

def with_retry(
    retry_config: Optional[RetryConfig] = None,
    dlq: Optional[DeadLetterQueue] = None,
    should_retry: Optional[Callable[[Exception], bool]] = None
):
    """
    Decorator for adding retry logic with exponential backoff to async functions
    
    Args:
        retry_config: Configuration for retry behavior
        dlq: Dead letter queue for failed messages
        should_retry: Function to determine if an exception should be retried
    
    Returns:
        Decorated function with retry logic
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retry_config.max_retries + 1):
                try:
                    if attempt > 0:
                        # Calculate delay with exponential backoff and optional jitter
                        delay = min(
                            retry_config.initial_delay * (retry_config.backoff_factor ** (attempt - 1)),
                            retry_config.max_delay
                        )
                        
                        if retry_config.jitter:
                            # Add ±10% jitter
                            delay *= (0.9 + 0.2 * (time.time() % 1))
                        
                        logger.info(f"Retry attempt {attempt}/{retry_config.max_retries} after {delay:.2f}s delay")
                        await asyncio.sleep(delay)
                    
                    return await func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this exception
                    if should_retry and not should_retry(e):
                        logger.warning(f"Non-retryable exception: {e}")
                        break
                    
                    if attempt < retry_config.max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{retry_config.max_retries} failed: {e}. "
                            f"Retrying..."
                        )
                    else:
                        logger.error(
                            f"All {retry_config.max_retries} attempts failed. Last error: {e}"
                        )
                        break
            
            # If we have a DLQ and this was a message processing failure, send to DLQ
            if dlq and last_exception:
                # Try to extract message data from args/kwargs
                message_data = {}
                if args and len(args) > 0 and hasattr(args[0], 'data'):
                    try:
                        message_data = json.loads(args[0].data.decode())
                    except:
                        message_data = {"raw_data": str(args[0].data)}
                
                context = {
                    "function": func.__name__,
                    "attempts": retry_config.max_retries + 1,
                    "timestamp": time.time()
                }
                
                await dlq.send_to_dlq(message_data, last_exception, context)
            
            # Re-raise the last exception if all retries failed
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

def should_retry_transient_error(exception: Exception) -> bool:
    """
    Default function to determine if an exception should be retried.
    Retry on network errors, timeouts, and temporary service unavailability.
    """
    error_type = type(exception).__name__
    error_msg = str(exception).lower()
    
    # Retry on these error types
    retryable_errors = {
        'TimeoutError', 'ConnectionError', 'NetworkError', 'ServiceUnavailableError',
        'RateLimitError', 'TemporaryError'
    }
    
    # Don't retry on these error types
    non_retryable_errors = {
        'ValidationError', 'AuthenticationError', 'AuthorizationError',
        'NotFoundError', 'InvalidRequestError'
    }
    
    # Check error type
    if error_type in retryable_errors:
        return True
    if error_type in non_retryable_errors:
        return False
    
    # Check error message patterns
    retryable_patterns = [
        'timeout', 'connection', 'network', 'temporary', 'unavailable',
        'rate limit', 'too many requests', 'service down', 'retry later'
    ]
    
    non_retryable_patterns = [
        'invalid', 'validation', 'auth', 'unauthorized', 'not found',
        'permission denied', 'bad request', 'malformed'
    ]
    
    for pattern in retryable_patterns:
        if pattern in error_msg:
            return True
    
    for pattern in non_retryable_patterns:
        if pattern in error_msg:
            return False
    
    # Default to retry for unknown errors
    return True

# Default retry configuration
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    initial_delay=1.0,
    max_delay=60.0,
    backoff_factor=2.0,
    jitter=True
)

