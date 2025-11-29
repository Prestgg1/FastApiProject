# tests/doctor_category/conftest.py
"""
Doctor Category Test Fixtures

Provides sample doctor category data for testing.
"""

from datetime import datetime, timezone

import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession

from models.doctor_category import DoctorCategory


@pytest_asyncio.fixture(name="sample_doctor_categories")
async def sample_doctor_categories_fixture(
    session: AsyncSession,
) -> list[DoctorCategory]:
    """
    Create sample doctor categories for testing.
    
    Returns:
        list[DoctorCategory]: 5 sample categories with different specialties
    """
    categories = [
        DoctorCategory(
            title="Kardiologiya",
            slug="kardiologiya",
            keywords="ürək, qan dövranı, kardiovaskulyar",
            image="cardiology.jpg",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        DoctorCategory(
            title="Nevrologiya",
            slug="nevrologiya",
            keywords="beyin, sinir sistemi, migren",
            image="neurology.jpg",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        DoctorCategory(
            title="Pediatriya",
            slug="pediatriya",
            keywords="uşaq, körpə, yeniyetmə",
            image="pediatrics.jpg",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        DoctorCategory(
            title="Dermatoloji",
            slug="dermatoloji",
            keywords="dəri, saç, dırnaq",
            image="dermatology.jpg",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        DoctorCategory(
            title="Oftalmologiya",
            slug="oftalmologiya",
            keywords="göz, görmə, lens",
            image="ophthalmology.jpg",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]

    for category in categories:
        session.add(category)
    
    await session.commit()

    for category in categories:
        await session.refresh(category)

    return categories


@pytest_asyncio.fixture(name="single_doctor_category")
async def single_doctor_category_fixture(
    session: AsyncSession,
) -> DoctorCategory:
    """
    Create a single doctor category for specific tests.
    
    Returns:
        DoctorCategory: Single cardiology category
    """
    category = DoctorCategory(
        title="Test Kardiologiya",
        slug="test-kardiologiya",
        keywords="test, ürək, kardio",
        image="test-cardiology.jpg",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    session.add(category)
    await session.commit()
    await session.refresh(category)

    return category