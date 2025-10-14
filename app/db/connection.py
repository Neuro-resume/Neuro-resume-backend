"""Database connection and session management using SQLAlchemy async."""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

# Global engine instance
engine: AsyncEngine | None = None

# Async session factory
async_session_maker: sessionmaker | None = None


async def init_db() -> None:
    """Initialize database connection and create engine."""
    global engine, async_session_maker

    try:
        logger.info("Initializing database connection...")

        # Create async engine
        engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,  # Log SQL queries in debug mode
            pool_pre_ping=True,  # Verify connections before using
            pool_size=10,
            max_overflow=20,
        )

        # Create async session factory
        async_session_maker = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        logger.info("Database connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database connection: {e}")
        raise


async def close_db() -> None:
    """Close database connection and dispose engine."""
    global engine

    if engine is not None:
        try:
            logger.info("Closing database connection...")
            await engine.dispose()
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: Database session for async operations
    """
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """
    Check if database connection is alive.

    Returns:
        bool: True if connection is healthy, False otherwise
    """
    if engine is None:
        return False

    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
