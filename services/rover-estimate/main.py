
"""
Rover Estimate Service
Listens for rfp.parsed events and computes baseline estimates
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
import nats
from nats.errors import TimeoutError
from libs.py.aec_shared.events import NATSEventPublisher
from libs.py.aec_shared.models import RfpParsedEvent, EstimateReadyEvent, Estimate, EstimateItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RoverEstimateNATSConsumer:
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

    async def subscribe_to_rfp_parsed(self):
        """Subscribe to rfp.parsed events"""
        if not self.nc:
            await self.connect()

        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                logger.info(f"Received RFP parsed event: {data.get('rfp', {}).get('id', 'unknown')}")
                
                # Compute baseline estimate
                estimate = await self.compute_estimate(data)
                
                # Publish estimate.ready event
                await self.publish_estimate_ready(estimate)
                
            except Exception as e:
                logger.error(f"Error processing RFP parsed event: {e}")

        # Subscribe to rfp.parsed topic
        await self.nc.subscribe("rfp.parsed", cb=message_handler)
        logger.info("Subscribed to rfp.parsed events")

    async def compute_estimate(self, rfp_data: dict) -> Estimate:
        """
        Compute baseline estimate from parsed RFP data
        """
        rfp = rfp_data.get('rfp', {})
        parsed_items = rfp_data.get('parsedItems', [])
        
        logger.info(f"Computing estimate for RFP: {rfp.get('id')}")
        
        # Convert parsed items to estimate items
        estimate_items = []
        total_amount = 0.0
        
        for item in parsed_items:
            quantity = item.get('quantity', 1)
            unit_cost = item.get('estimated_cost', 0)
            total_cost = quantity * unit_cost
            
            estimate_item = EstimateItem(
                id=str(uuid.uuid4()),
                description=item.get('description', ''),
                quantity=quantity,
                unit=item.get('unit', 'ea'),
                unit_cost=unit_cost,
                total_cost=total_cost,
                category=item.get('category', 'general')
            )
            
            estimate_items.append(estimate_item)
            total_amount += total_cost
        
        # Create estimate
        estimate = Estimate(
            id=str(uuid.uuid4()),
            project_id=rfp.get('projectId', ''),
            rfp_id=rfp.get('id', ''),
            version=1,
            status="ready",
            total_amount=total_amount,
            items=estimate_items,
            notes=f"Baseline estimate computed from RFP {rfp.get('filename')}",
            org_id=rfp.get('orgId', 'demo-org')
        )
        
        logger.info(f"Computed estimate {estimate.id} with total: ${total_amount:,.2f}")
        return estimate

    async def publish_estimate_ready(self, estimate: Estimate):
        """Publish estimate.ready event"""
        try:
            event = EstimateReadyEvent(estimate=estimate)
            await self.publisher.publish_event("estimate.ready", event.dict())
            logger.info(f"Published estimate.ready event for estimate: {estimate.id}")
        except Exception as e:
            logger.error(f"Failed to publish estimate.ready event: {e}")

    async def run(self):
        """Run the NATS consumer"""
        try:
            await self.connect()
            await self.subscribe_to_rfp_parsed()
            
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
    consumer = RoverEstimateNATSConsumer()
    await consumer.run()

if __name__ == "__main__":
    asyncio.run(main())
