

"""
Database migration for Row Level Security (RLS) policies
Enables multi-tenant data isolation at the database level
"""

import asyncio
from sqlalchemy import text
from db import engine

async def run_migration():
    async with engine.connect() as conn:
        # Enable RLS on all tables
        tables = ["projects", "rfp_artifacts", "estimates"]
        
        for table in tables:
            # Enable RLS on the table
            await conn.execute(text(f"""
                ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;
            """))
            
            # Create policy that allows users to see only their organization's data
            await conn.execute(text(f"""
                CREATE POLICY {table}_org_isolation_policy ON {table}
                FOR ALL
                USING (org_id = current_setting('app.current_org_id', true));
            """))
            
            # Create policy that allows service accounts (system role) to see all data
            await conn.execute(text(f"""
                CREATE POLICY {table}_system_access_policy ON {table}
                FOR ALL
                USING (current_setting('app.current_user_role', true) = 'system');
            """))
        
        # Create audit_log table for tracking access and changes
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id UUID PRIMARY KEY,
                org_id VARCHAR(100) NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                action VARCHAR(50) NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                resource_id VARCHAR(100),
                details JSONB,
                trace_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_audit_log_org_id (org_id),
                INDEX idx_audit_log_user_id (user_id),
                INDEX idx_audit_log_created_at (created_at)
            )
        """))
        
        # Enable RLS on audit_log table
        await conn.execute(text("""
            ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
        """))
        
        # Policy for audit_log - users can only see their own organization's audit logs
        await conn.execute(text("""
            CREATE POLICY audit_log_org_isolation_policy ON audit_log
            FOR ALL
            USING (org_id = current_setting('app.current_org_id', true));
        """))
        
        # System can see all audit logs
        await conn.execute(text("""
            CREATE POLICY audit_log_system_access_policy ON audit_log
            FOR ALL
            USING (current_setting('app.current_user_role', true) = 'system');
        """))
        
        await conn.commit()
        print("RLS policies and audit_log table created successfully")

if __name__ == "__main__":
    asyncio.run(run_migration())

