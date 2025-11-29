from datetime import datetime, timezone
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from database import get_db
from dependencies.auth import require_admin
from main import app as main_app
from models import Blog, Customer, User
from models.user import UserRole
from schemas.user_schema import UserBase
from services import CryptoService


# ✅ Async engine
@pytest_asyncio.fixture(name="engine")
async def engine_fixture():
    """Test üçün in-memory async SQLite database"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Test zamanı SQL logları gizlət
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


# ✅ Async session factory
@pytest_asyncio.fixture(name="session_factory")
async def session_factory_fixture(engine):
    """Async session factory"""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# ✅ Async session
@pytest_asyncio.fixture(name="session")
async def session_fixture(session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Test database session (ASYNC)"""
    async with session_factory() as session:
        yield session


# ✅ Async client
@pytest_asyncio.fixture(name="client")
async def client_fixture(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Async test client"""

    async def get_test_db():
        yield session

    main_app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(
        transport=ASGITransport(app=main_app), base_url="http://test"
    ) as client:
        yield client

    main_app.dependency_overrides.clear()


# ✅ Admin async client
@pytest_asyncio.fixture(name="admin_client")
async def admin_client_fixture(
    session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Admin async test client (bypass auth)"""

    async def get_test_db():
        yield session

    # Mock admin user
    def mock_require_admin():
        return {"id": 1, "email": "admin@test.com", "role": "admin"}

    main_app.dependency_overrides[get_db] = get_test_db
    main_app.dependency_overrides[require_admin] = mock_require_admin

    async with AsyncClient(
        transport=ASGITransport(app=main_app), base_url="http://test"
    ) as client:
        yield client

    main_app.dependency_overrides.clear()

