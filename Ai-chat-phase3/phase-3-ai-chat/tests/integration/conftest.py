"""Integration test configuration."""

import os
import pytest
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

# Set test environment before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-key-for-integration-tests"
os.environ["APP_ENV"] = "test"

from src.api.main import app
from src.db.connection import get_session


@pytest.fixture
async def test_app_with_db(async_engine):
    """Create app with test database override."""
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create session maker
    SessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Override dependency
    async def override_get_session():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    # Override lifespan to skip database initialization
    @asynccontextmanager
    async def test_lifespan(app):
        # Skip startup initialization - db already ready
        yield
        # Skip shutdown - db cleanup handled by fixture

    app.lifespan = test_lifespan

    yield app

    # Cleanup
    app.dependency_overrides.clear()
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
def client(test_app_with_db):
    """FastAPI test client with test database."""
    return TestClient(test_app_with_db)


@pytest.fixture
async def session(test_app_with_db, async_engine):
    """Get async session for direct database testing."""
    SessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with SessionLocal() as session:
        yield session
