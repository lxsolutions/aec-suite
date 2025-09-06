"""
NATS Consumer service for BuildForge
Listens for rfp.parsed events and generates estimates
"""

import asyncio
import json
import logging
from typing import Optional
import nats
from nats.errors import TimeoutError
from libs.py.aec_shared.events import NATSEventPublisher
from libs.py.aec_shared.models import RfpParsedEvent, EstimateReadyEvent
from libs.py.aec_shared.retry import with_retry, RetryConfig, DeadLetterQueue, should_retry_transient_error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuildForgeNATSConsumer:
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc = None
        self.publisher = NATSEventPublisher(nats_url)
        self.dlq = DeadLetterQueue()
        self.retry_config = RetryConfig(
            max_retries=3,
            initial_delay=2.0,
            max_delay=30.0,
            backoff_factor=2.0,
            jitter=True
        )

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
                logger.info(f"Received RFP parsed event: {data}")
                
                # Process the RFP and generate estimate
                estimate = await self.generate_estimate(data)
                
                # Publish estimate.ready event
                await self.publish_estimate_ready(estimate)
                
            except Exception as e:
                logger.error(f"Error processing RFP parsed event: {e}")

        # Subscribe to rfp.parsed topic
        await self.nc.subscribe("rfp.parsed", cb=message_handler)
        logger.info("Subscribed to rfp.parsed events")

    @with_retry(
        retry_config=RetryConfig(
            max_retries=3,
            initial_delay=2.0,
            max_delay=30.0,
            backoff_factor=2.0,
            jitter=True
        ),
        should_retry=should_retry_transient_error
    )
    async def generate_estimate(self, rfp_data: dict) -> dict:
        """
        Generate estimate from parsed RFP data
        This is a simplified version - in production, this would use
        the existing BuildForge estimation logic
        """
        logger.info(f"Generating estimate for RFP: {rfp_data.get('filename')}")
        
        # Mock estimate generation based on parsed items
        parsed_items = rfp_data.get('parsed_items', [])
        
        estimate_items = []
        total_amount = 0
        
        for item in parsed_items:
            # Convert parsed item to estimate line item
            unit_cost = item.get('estimated_cost', 0)
            quantity = item.get('quantity', 1)
            total_cost = unit_cost * quantity
            
            estimate_item = {
                "code": item.get('item_code', 'UNK001'),
                "description": item.get('description', 'Unknown item'),
                "quantity": quantity,
                "unit": item.get('unit', 'ea'),
                "unit_cost": unit_cost,
                "total_cost": total_cost,
                "category": "construction"
            }
            
            estimate_items.append(estimate_item)
            total_amount += total_cost
        
        # Create mock schedule
        schedule = {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-12-31T23:59:59Z",
            "milestones": [
                {"name": "Design Complete", "date": "2024-03-01T00:00:00Z"},
                {"name": "Foundation Complete", "date": "2024-06-01T00:00:00Z"},
                {"name": "Structure Complete", "date": "2024-09-01T00:00:00Z"},
                {"name": "Project Complete", "date": "2024-12-31T23:59:59Z"}
            ]
        }
        
        return {
            "rfp_id": rfp_data.get('id', 'unknown-rfp'),
            "project_id": rfp_data.get('project_id', 'unknown-project'),
            "version": 1,
            "status": "ready",
            "total_amount": total_amount,
            "items": estimate_items,
            "schedule": schedule,
            "notes": "Auto-generated estimate from RFP parsing"
        }


    @with_retry(
        retry_config=RetryConfig(
            max_retries=3,
            initial_delay=1.0,
            max_delay=10.0,
            backoff_factor=2.0,
            jitter=True
        ),
        should_retry=should_retry_transient_error
    )
    async def publish_estimate_ready(self, estimate_data: dict):
        """Publish estimate.ready event with retry logic"""
        event = EstimateReadyEvent(
            estimate=estimate_data,
            schedule=estimate_data.get('schedule')
        )
        await self.publisher.publish_estimate_ready(event)
        logger.info(f"Published estimate.ready event for estimate: {estimate_data.get('rfp_id')}")

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
    consumer = BuildForgeNATSConsumer()
    await consumer.run()

if __name__ == "__main__":
    asyncio.run(main())
