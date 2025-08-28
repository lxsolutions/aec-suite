


"""
NATS event client for publishing and consuming messages
"""

import json
from typing import Any, Dict, Optional
import nats
from nats.aio.client import Client as NATS
from nats.js.client import JetStreamContext

from .config import settings

class NATSClient:
    """NATS client for event-driven communication"""
    
    def __init__(self):
        self.nc: Optional[NATS] = None
        self.js: Optional[JetStreamContext] = None
    
    async def connect(self) -> None:
        """Connect to NATS server"""
        try:
            self.nc = await nats.connect(settings.NATS_URL)
            self.js = self.nc.jetstream()
            print(f"Connected to NATS at {settings.NATS_URL}")
        except Exception as e:
            print(f"Failed to connect to NATS: {e}")
            raise
    
    async def close(self) -> None:
        """Close NATS connection"""
        if self.nc:
            await self.nc.close()
    
    async def publish(self, subject: str, data: Dict[str, Any]) -> None:
        """Publish message to NATS subject"""
        if not self.nc:
            raise RuntimeError("NATS client not connected")
        
        try:
            message = json.dumps(data)
            await self.nc.publish(subject, message.encode())
        except Exception as e:
            print(f"Failed to publish message: {e}")
            raise
    
    async def publish_jetstream(self, subject: str, data: Dict[str, Any]) -> None:
        """Publish message to JetStream with persistence"""
        if not self.js:
            raise RuntimeError("JetStream not available")
        
        try:
            message = json.dumps(data)
            await self.js.publish(subject, message.encode())
        except Exception as e:
            print(f"Failed to publish to JetStream: {e}")
            raise
    
    async def subscribe(self, subject: str, callback) -> None:
        """Subscribe to NATS subject"""
        if not self.nc:
            raise RuntimeError("NATS client not connected")
        
        try:
            await self.nc.subscribe(subject, cb=callback)
        except Exception as e:
            print(f"Failed to subscribe: {e}")
            raise

# Global NATS client instance
nats_client = NATSClient()


