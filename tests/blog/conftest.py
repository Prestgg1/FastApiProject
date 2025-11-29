from sqlmodel.ext.asyncio.session import AsyncSession
from models.blog import Blog
import pytest_asyncio

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

