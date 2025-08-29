

"""
Seed script for demo data
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy import text
from services.gateway.db import engine

async def seed_demo_data():
    async with engine.connect() as conn:
        # Create demo project
        project_id = str(uuid.uuid4())
        await conn.execute(text("""
            INSERT INTO projects (id, name, description, client_id, start_date, end_date, budget, status, org_id)
            VALUES (:id, :name, :description, :client_id, :start_date, :end_date, :budget, :status, :org_id)
        """), {
            "id": project_id,
            "name": "Demo Office Building",
            "description": "A 5-story office building with parking garage",
            "client_id": "client-001",
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=365),
            "budget": 2500000.0,
            "status": "active",
            "org_id": "demo-org"
        })

        # Create demo RFP
        rfp_id = str(uuid.uuid4())
        await conn.execute(text("""
            INSERT INTO rfp_artifacts (id, project_id, filename, original_filename, file_size, mime_type, status, org_id)
            VALUES (:id, :project_id, :filename, :original_filename, :file_size, :mime_type, :status, :org_id)
        """), {
            "id": rfp_id,
            "project_id": project_id,
            "filename": "rfp_demo_office.pdf",
            "original_filename": "Office_Building_RFP.pdf",
            "file_size": 1024000,
            "mime_type": "application/pdf",
            "status": "parsed",
            "org_id": "demo-org"
        })

        # Create demo estimate
        estimate_id = str(uuid.uuid4())
        estimate_items = [
            {"code": "SITE01", "description": "Site Preparation", "quantity": 1, "unit": "ls", "unit_cost": 50000, "total_cost": 50000},
            {"code": "FND01", "description": "Foundation Work", "quantity": 1, "unit": "ls", "unit_cost": 150000, "total_cost": 150000},
            {"code": "STR01", "description": "Structural Steel", "quantity": 200, "unit": "ton", "unit_cost": 2500, "total_cost": 500000},
            {"code": "EXT01", "description": "Exterior Finishes", "quantity": 1, "unit": "ls", "unit_cost": 300000, "total_cost": 300000},
            {"code": "INT01", "description": "Interior Finishes", "quantity": 1, "unit": "ls", "unit_cost": 400000, "total_cost": 400000},
            {"code": "MEP01", "description": "MEP Systems", "quantity": 1, "unit": "ls", "unit_cost": 600000, "total_cost": 600000}
        ]

        await conn.execute(text("""
            INSERT INTO estimates (id, project_id, rfp_id, version, status, total_amount, items, notes, org_id)
            VALUES (:id, :project_id, :rfp_id, :version, :status, :total_amount, :items, :notes, :org_id)
        """), {
            "id": estimate_id,
            "project_id": project_id,
            "rfp_id": rfp_id,
            "version": 1,
            "status": "ready",
            "total_amount": 2000000.0,
            "items": estimate_items,
            "notes": "Initial estimate based on RFP requirements",
            "org_id": "demo-org"
        })

        await conn.commit()
        print(f"Demo data seeded successfully!")
        print(f"Project ID: {project_id}")
        print(f"RFP ID: {rfp_id}")
        print(f"Estimate ID: {estimate_id}")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())

