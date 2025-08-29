
"""
NATS event publishing and consumption utilities
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable, Awaitable, List
from uuid import UUID, uuid4

import nats
from nats.aio.client import Client as NATSClient
from nats.js.client import JetStreamContext
from pydantic import BaseModel

from .models import Project, Rfp, Estimate, Schedule


logger = logging.getLogger(__name__)


class NATSEventPublisher:
    """NATS event publisher with JetStream support"""
    
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc: Optional[NATSClient] = None
        self.js: Optional[JetStreamContext] = None
    
    async def connect(self) -> None:
        """Connect to NATS server"""
        try:
            self.nc = await nats.connect(self.nats_url)
            self.js = self.nc.jetstream()
            logger.info(f"Connected to NATS at {self.nats_url}")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise
    
    async def close(self) -> None:
        """Close NATS connection"""
        if self.nc:
            await self.nc.close()
            logger.info("NATS connection closed")
    
    async def publish_event(self, subject: str, event_data: Dict[str, Any]) -> None:
        """Publish an event to NATS"""
        if not self.nc or not self.js:
            raise RuntimeError("NATS client not connected")
        
        try:
            event = {
                "id": str(uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "data": event_data
            }
            await self.js.publish(subject, json.dumps(event).encode())
            logger.info(f"Published event to {subject}: {event_data}")
        except Exception as e:
            logger.error(f"Failed to publish event to {subject}: {e}")
            raise


class NATSEventConsumer:
    """NATS event consumer with JetStream support"""
    
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc: Optional[NATSClient] = None
        self.js: Optional[JetStreamContext] = None
    
    async def connect(self) -> None:
        """Connect to NATS server"""
        try:
            self.nc = await nats.connect(self.nats_url)
            self.js = self.nc.jetstream()
            logger.info(f"Connected to NATS at {self.nats_url}")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise
    
    async def close(self) -> None:
        """Close NATS connection"""
        if self.nc:
            await self.nc.close()
            logger.info("NATS connection closed")
    
    async def subscribe(
        self,
        subject: str,
        callback: Callable[[Dict[str, Any]], Awaitable[None]],
        durable_name: Optional[str] = None,
        queue_group: Optional[str] = None
    ) -> None:
        """Subscribe to events from NATS"""
        if not self.nc or not self.js:
            raise RuntimeError("NATS client not connected")
        
        try:
            sub = await self.js.subscribe(
                subject,
                durable=durable_name,
                queue=queue_group,
                cb=lambda msg: self._handle_message(msg, callback)
            )
            logger.info(f"Subscribed to {subject}")
            return sub
        except Exception as e:
            logger.error(f"Failed to subscribe to {subject}: {e}")
            raise
    
    async def _handle_message(self, msg, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Handle incoming NATS message"""
        try:
            event_data = json.loads(msg.data.decode())
            await callback(event_data)
            await msg.ack()
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            await msg.nak()


# Event schemas for AsyncAPI
class ProjectCreatedEvent(BaseModel):
    project: Project


class RfpParsedEvent(BaseModel):
    rfp: Rfp
    parsed_items: List[Dict[str, Any]]


class EstimateReadyEvent(BaseModel):
    estimate: Estimate
    schedule: Optional[Schedule] = None


class ScheduleUpdatedEvent(BaseModel):
    schedule: Schedule


class ERPSyncCompletedEvent(BaseModel):
    estimate_id: UUID
    erp_id: str
    sync_timestamp: datetime


# Global NATS client instance
nats_publisher = NATSEventPublisher()
nats_consumer = NATSEventConsumer()
