

"""
Initial database migration for Gateway service
"""

import asyncio
from sqlalchemy import text
from db import engine

async def run_migration():
    async with engine.connect() as conn:
        # Create tables if they don't exist
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS projects (
                id UUID PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                client_id VARCHAR(100) NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP,
                budget FLOAT,
                status VARCHAR(20) DEFAULT 'draft',
                org_id VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rfp_artifacts (
                id UUID PRIMARY KEY,
                project_id UUID REFERENCES projects(id),
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type VARCHAR(100) NOT NULL,
                status VARCHAR(20) DEFAULT 'received',
                parsed_data JSONB,
                error_message TEXT,
                org_id VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS estimates (
                id UUID PRIMARY KEY,
                project_id UUID REFERENCES projects(id),
                rfp_id UUID REFERENCES rfp_artifacts(id),
                version INTEGER DEFAULT 1,
                status VARCHAR(20) DEFAULT 'draft',
                total_amount FLOAT DEFAULT 0.0,
                items JSONB,
                notes VARCHAR(500),
                org_id VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        await conn.commit()
        print("Database migration completed successfully")

if __name__ == "__main__":
    asyncio.run(run_migration())

