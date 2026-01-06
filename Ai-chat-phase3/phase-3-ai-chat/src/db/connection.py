"""PostgreSQL connection pool management."""

import os
from typing import Optional, AsyncGenerator
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from pydantic_settings import BaseSettings

from src.utils.errors import DatabaseError


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    class Config:
        env_file = ".env"
        extra = "ignore"  # Pydantic v2: Allow extra fields from .env


# Global engine and session maker
engine = None
async_session_maker = None


async def init_db() -> None:
    """Initialize database engine and create tables."""
    global engine, async_session_maker

    settings = DatabaseSettings()
    database_url = settings.database_url

    try:
        # Create async engine
        engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
        )

        # Create session maker
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    except Exception as e:
        raise DatabaseError(
            f"Failed to initialize database: {str(e)}",
            user_message="Database initialization failed. Please check configuration.",
            context={"error": str(e)},
        )


async def close_db() -> None:
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    if not async_session_maker:
        raise DatabaseError(
            "Database not initialized",
            user_message="Database connection not available",
        )

    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise DatabaseError(
                f"Database session error: {str(e)}",
                user_message="Database operation failed. Please try again.",
                context={"error": str(e)},
            )
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """Get a database session (for non-dependency scenarios)."""
    if not async_session_maker:
        raise DatabaseError(
            "Database not initialized",
            user_message="Database connection not available",
        )
    return async_session_maker()
