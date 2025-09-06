

"""
Database connection and utilities for Gateway service
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

from core.config import settings

logger = logging.getLogger(__name__)

# Database engine and session factory
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

from fastapi import Request
from typing import Optional
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db(request: Optional[Request] = None) -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with RLS context"""
    async with AsyncSessionLocal() as session:
        try:
            # Set RLS context if request is provided and user is authenticated
            if request and hasattr(request.state, 'user'):
                user = request.state.user
                await session.execute(
                    text("SELECT set_config('app.current_org_id', :org_id, false)"),
                    {"org_id": user.org_id}
                )
                await session.execute(
                    text("SELECT set_config('app.current_user_role', :role, false)"),
                    {"role": user.roles[0].value if user.roles else 'none'}
                )
            
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")

async def close_db() -> None:
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")

