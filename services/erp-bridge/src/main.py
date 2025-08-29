
"""
ERP Bridge Service
Listens for estimate.ready events and syncs with ERP systems
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
import nats
from nats.errors import TimeoutError
from libs.py.aec_shared.events import NATSEventPublisher
from libs.py.aec_shared.models import EstimateReadyEvent, ERPSyncCompletedEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ERPBridgeNATSConsumer:
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc = None
        self.publisher = NATSEventPublisher(nats_url)

    async def connect(self):
        """Connect to NATS server"""
        try:
            self.nc = await nats.connect(self.nats_url)
            logger.info(f"Connected to NATS server at {self.nats_url}")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise

    async def subscribe_to_estimate_ready(self):
        """Subscribe to estimate.ready events"""
        if not self.nc:
            await self.connect()

        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                logger.info(f"Received estimate ready event: {data.get('estimate', {}).get('id', 'unknown')}")
                
                # Sync estimate with ERP system
                erp_id = await self.sync_with_erp(data)
                
                # Publish erp.sync.completed event
                await self.publish_erp_sync_completed(data.get('estimate', {}).get('id'), erp_id)
                
            except Exception as e:
                logger.error(f"Error processing estimate ready event: {e}")

        # Subscribe to estimate.ready topic
        await self.nc.subscribe("estimate.ready", cb=message_handler)
        logger.info("Subscribed to estimate.ready events")

    async def sync_with_erp(self, estimate_data: dict) -> str:
        """
        Sync estimate with ERP system (mock implementation)
        In production, this would integrate with Acumatica, Odoo, etc.
        """
        estimate = estimate_data.get('estimate', {})
        estimate_id = estimate.get('id', 'unknown-estimate')
        
        logger.info(f"Syncing estimate {estimate_id} with ERP system")
        
        # Mock ERP integration - generate a fake ERP ID
        erp_id = f"ERP-{uuid.uuid4().hex[:8].upper()}"
        
        # Simulate some processing time
        await asyncio.sleep(0.5)
        
        logger.info(f"Estimate {estimate_id} synced to ERP with ID: {erp_id}")
        return erp_id

    async def publish_erp_sync_completed(self, estimate_id: str, erp_id: str):
        """Publish erp.sync.completed event"""
        try:
            event = ERPSyncCompletedEvent(
                estimateId=estimate_id,
                erpId=erp_id,
                syncTimestamp=datetime.utcnow().isoformat() + "Z"
            )
            await self.publisher.publish_erp_sync_completed(event)
            logger.info(f"Published erp.sync.completed event for estimate: {estimate_id}")
        except Exception as e:
            logger.error(f"Failed to publish erp.sync.completed event: {e}")

    async def run(self):
        """Run the NATS consumer"""
        try:
            await self.connect()
            await self.subscribe_to_estimate_ready()
            
            # Keep the consumer running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"NATS consumer failed: {e}")
        finally:
            if self.nc:
                await self.nc.close()

async def main():
    """Main function"""
    consumer = ERPBridgeNATSConsumer()
    await consumer.run()

if __name__ == "__main__":
    asyncio.run(main())
