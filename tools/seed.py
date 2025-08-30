#!/usr/bin/env python3
"""
Seed script for AEC Suite database.
Creates initial organization, admin user, project, and estimate.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Import models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'aec-orchestrator', 'backend', 'src'))

from backend.models import Base, Organization, User, Project, Estimate, UserRole

# Database configuration
DATABASE_URL = "postgresql+asyncpg://aec:aec123@localhost:5432/aec_suite"
SYNC_DATABASE_URL = "postgresql://aec:aec123@localhost:5432/aec_suite"

async def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    # Connect to postgres database to create our database
    engine = create_engine(SYNC_DATABASE_URL.replace('aec_suite', 'postgres'))
    conn = engine.connect()
    conn.execute(text("COMMIT"))  # End any existing transaction
    
    # Check if database exists
    result = conn.execute(
        text("SELECT 1 FROM pg_database WHERE datname = 'aec_suite'")
    )
    exists = result.scalar() is not None
    
    if not exists:
        print("Creating database aec_suite...")
        conn.execute(text("CREATE DATABASE aec_suite"))
        print("Database created successfully")
    
    conn.close()
    engine.dispose()

async def seed_database():
    """Seed the database with initial data"""
    print("Starting database seeding...")
    
    # Create database if it doesn't exist
    await create_database_if_not_exists()
    
    # Create async engine and session
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        try:
            # Check if organization already exists
            existing_org = await session.execute(
                text("SELECT id FROM organizations WHERE slug = 'demo-org'")
            )
            org_exists = existing_org.scalar() is not None
            
            if org_exists:
                print("Demo organization already exists. Skipping seeding.")
                return
            
            # Create organization
            org = Organization(
                id=uuid.uuid4(),
                name="Demo Organization",
                slug="demo-org",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(org)
            await session.flush()
            
            # Create admin user
            admin_user = User(
                id=uuid.uuid4(),
                email="admin@demo.org",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
                is_active=True,
                is_superuser=True,
                is_verified=True,
                role=UserRole.ADMIN,
                org_id=org.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(admin_user)
            await session.flush()
            
            # Create project
            project = Project(
                id=uuid.uuid4(),
                name="Demo Construction Project",
                org_id=org.id,
                data={
                    "type": "commercial",
                    "location": "123 Main St, Anytown, USA",
                    "square_feet": 10000,
                    "floors": 2
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(project)
            await session.flush()
            
            # Create estimate
            estimate = Estimate(
                id=uuid.uuid4(),
                project_id=project.id,
                org_id=org.id,
                name="Initial Construction Estimate",
                description="Comprehensive estimate for demo construction project including materials, labor, and equipment",
                material_cost=250000.0,
                labor_cost=150000.0,
                equipment_cost=50000.0,
                subcontractor_cost=75000.0,
                overhead_cost=30000.0,
                profit_margin=0.15,
                total_cost=555000.0,
                status="draft",
                version=1,
                created_by=admin_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(estimate)
            
            await session.commit()
            print("Database seeded successfully!")
            print(f"Organization: {org.name} ({org.slug})")
            print(f"Admin User: {admin_user.email}")
            print(f"Project: {project.name}")
            print(f"Estimate: {estimate.name} - ${estimate.total_cost:,.2f}")
            
        except Exception as e:
            await session.rollback()
            print(f"Error seeding database: {e}")
            raise

async def main():
    """Main function"""
    try:
        await seed_database()
    except Exception as e:
        print(f"Failed to seed database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
