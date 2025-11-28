import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from upstash_redis import Redis

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "")

if ENVIRONMENT == "development" and not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./dev_database.db"
    print(f"🔧 Development mode: Using SQLite at {DATABASE_URL}")
elif not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required for non-development environments"
    )
else:
    print(f"🚀 {ENVIRONMENT.capitalize()} mode: Using PostgreSQL")

if DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(
        DATABASE_URL,
        echo=True if ENVIRONMENT == "development" else False,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        echo=True if ENVIRONMENT == "development" else False,
    )
SessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
redis = Redis(
    os.getenv("UPSTASH_REDIS_REST_URL") or "",
    os.getenv("UPSTASH_REDIS_REST_TOKEN") or "",
)


async def get_db():
    async with AsyncSession(engine) as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_db)]


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def init_db():
    async with AsyncSession(engine):
        await create_tables()
