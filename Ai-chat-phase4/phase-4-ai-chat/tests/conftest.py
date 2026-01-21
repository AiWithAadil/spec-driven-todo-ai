"""Pytest configuration and fixtures."""

import os
import pytest
import asyncio
import jwt
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

# Set test environment
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-key-for-integration-tests"

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_engine():
    """Create async engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for testing."""
    SessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with SessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_user_id() -> str:
    """Test user ID."""
    return "test-user-123"


@pytest.fixture
def test_jwt_token(test_user_id: str) -> str:
    """Test JWT token."""
    jwt_secret = os.getenv("JWT_SECRET", "test-secret-key-for-integration-tests")
    token = jwt.encode(
        {"sub": test_user_id},
        jwt_secret,
        algorithm="HS256"
    )
    return f"Bearer {token}"
