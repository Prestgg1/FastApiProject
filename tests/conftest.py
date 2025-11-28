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


@pytest_asyncio.fixture(name="sample_blogs")
async def sample_blogs_fixture(session: AsyncSession) -> list[Blog]:
    from datetime import datetime, timezone

    blogs = [
        Blog(
            title="Python FastAPI",
            slug="python-fastapi",
            description="FastAPI tutorial",
            text="FastAPI is a modern web framework...",
            keywords="python, fastapi, web",
            status=True,
            created_at=datetime.now(timezone.utc),
        ),
        Blog(
            title="SQLModel Guide",
            slug="sqlmodel-guide",
            description="SQLModel ORM tutorial",
            text="SQLModel combines SQLAlchemy and Pydantic...",
            keywords="sqlmodel, orm, database",
            status=True,
            created_at=datetime.now(timezone.utc),
        ),
        Blog(
            title="Async Programming",
            slug="async-programming",
            description="Python async/await",
            text="Async programming in Python...",
            keywords="python, async, asyncio",
            status=False,
            created_at=datetime.now(timezone.utc),
        ),
    ]

    for blog in blogs:
        session.add(blog)
    await session.commit()

    for blog in blogs:
        await session.refresh(blog)

    return blogs


@pytest_asyncio.fixture(name="sample_customers")
async def sample_customers_fixture(session: AsyncSession):
    users_data = [
        {
            "name": "Aysel Məmmədova",
            "email": "aysel@example.com",
            "password": CryptoService.hash_password("password123"),
            "role": UserRole.customer,
            "status": True,
        },
        {
            "name": "Elvin Həsənov",
            "email": "elvin@example.com",
            "password": CryptoService.hash_password("password123"),
            "role": UserRole.customer,
            "status": True,
        },
        {
            "name": "Leyla Quliyeva",
            "email": "leyla@example.com",
            "password": CryptoService.hash_password("password123"),
            "role": UserRole.customer,
            "status": False,
        },
    ]

    users = []
    for user_data in users_data:
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            password= user_data["password"],
            role= UserRole.customer,
            status=user_data["status"]
        )
        session.add(user)
        users.append(user)

    await session.commit()

    for user in users:
        await session.refresh(user)

    customers_data = [
        {
            "user_id": users[0].id,
            "finCode": "1AABBCC",
            "phone": "+994501234567",
            "birthday": datetime(1995, 5, 15),
            "city": "Bakı",
            "region": "Nəsimi",
            "street": "28 May küçəsi",
            "address": "Bina 123, Mənzil 45",
            "gender": "female",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "user_id": users[1].id,
            "finCode": "2CCDDEE",
            "phone": "+994552345678",
            "birthday": datetime(1990, 8, 20),
            "city": "Bakı",
            "region": "Yasamal",
            "street": "Azadlıq prospekti",
            "address": "Bina 45, Mənzil 12",
            "gender": "male",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "user_id": users[2].id,
            "finCode": "3EEFFGG",
            "phone": "+994703456789",
            "birthday": datetime(1988, 12, 10),
            "city": "Gəncə",
            "region": "Kəpəz",
            "street": "Heydər Əliyev prospekti",
            "address": "Bina 78, Mənzil 23",
            "gender": "female",
            "created_at": datetime.now(timezone.utc),
        },
    ]

    customers = []
    for customer_data in customers_data:
        customer = Customer(**customer_data)
        session.add(customer)
        customers.append(customer)
    await session.commit()
    for customer in customers:
        await session.refresh(customer)
    return customers
