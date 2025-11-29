"""
Doctor Category Service Module

This module provides service layer methods for managing doctor categories.
All methods are static and can be called without instantiating the service class.
"""

from datetime import datetime
from typing import Any, Optional, Sequence

from fastapi import HTTPException
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select, or_

from database import Session
from models.doctor_category import DoctorCategory
from schemas.doctor_category_schema import (
    DoctorCategoryCreate,
    DoctorCategoryUpdate,
)


class DoctorCategoryService:
    """
    Service class for Doctor Category operations.
    
    This class provides static methods for CRUD operations on doctor categories.
    All methods are async and require an AsyncSession database connection.
    """

    @staticmethod
    async def create(
        doctor_category_data: DoctorCategoryCreate,
        db: AsyncSession
    ) -> DoctorCategory:
        """
        Create a new doctor category.

        Args:
            doctor_category_data (DoctorCategoryCreate): The data for creating a new category.
                Must include title, and optionally keywords and image.
            db (AsyncSession): The database session for executing queries.

        Returns:
            DoctorCategory: The newly created doctor category object.

        Example:
            ```python
            category_data = DoctorCategoryCreate(
                title="Cardiology",
                keywords=["heart", "cardiovascular"],
                image="cardiology.jpg"
            )
            new_category = await DoctorCategoryService.create(category_data, db)
            ```
        """
        slug = slugify(doctor_category_data.title)
        
        new_category = DoctorCategory(
            title=doctor_category_data.title,
            slug=slug,
            keywords=doctor_category_data.keywords,
            image=doctor_category_data.image,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        
        return new_category

    @staticmethod
    async def get_all(db: Session) -> Sequence[DoctorCategory]:
        """
        Retrieve all doctor categories.

        Args:
            db (Session): The database session for executing queries.

        Returns:
            list[DoctorCategory]: A list of all doctor category objects.

        Example:
            ```python
            categories = await DoctorCategoryService.get_all(db)
            for category in categories:
                print(category.title)
            ```
        """
        result = await db.exec(select(DoctorCategory))
        return result.all()

    @staticmethod
    async def get_all_partial(
        db: Session
    ) -> Sequence[dict[str, Any]]:
        """
        Retrieve partial data for all doctor categories (id, title, slug, image only).

        Args:
            db (Session): The database session for executing queries.

        Returns:
            list[dict]: A list of dictionaries containing id, title, slug, and image.

        Example:
            ```python
            categories = await DoctorCategoryService.get_all_partial(db)
            # Returns: [{"id": 1, "title": "Cardiology", "slug": "cardiology", "image": "..."}, ...]
            ```
        """
        result = await db.exec(
            select(
                DoctorCategory.id,
                DoctorCategory.title,
                DoctorCategory.slug,
                DoctorCategory.image
            )
        )
        
        return [
            {
                "id": row[0],
                "title": row[1],
                "slug": row[2],
                "image": row[3]
            }
            for row in result
        ]

    @staticmethod
    async def get_by_slug(
        slug: str,
        db: Session
    ) -> DoctorCategory:
        """
        Retrieve a doctor category by its slug.

        Args:
            slug (str): The unique slug identifier for the category.
            db (Session): The database session for executing queries.

        Returns:
            DoctorCategory: The doctor category object matching the slug.

        Raises:
            HTTPException: 404 error if the category is not found.

        Example:
            ```python
            category = await DoctorCategoryService.get_by_slug("cardiology", db)
            print(category.title)  # "Cardiology"
            ```
        """
        result = await db.exec(
            select(DoctorCategory).where(DoctorCategory.slug == slug)
        )
        doctor_category = result.first()
        
        if not doctor_category:
            raise HTTPException(
                status_code=404,
                detail=f"Doctor Category with slug '{slug}' not found"
            )
        
        return doctor_category

    @staticmethod
    async def get_by_id(
        category_id: int,
        db: Session
    ) -> Optional[DoctorCategory]:
        """
        Retrieve a doctor category by its ID.

        Args:
            category_id (int): The unique ID of the category.
            db (AsyncSession): The database session for executing queries.

        Returns:
            Optional[DoctorCategory]: The doctor category object if found, None otherwise.

        Example:
            ```python
            category = await DoctorCategoryService.get_by_id(1, db)
            if category:
                print(category.title)
            ```
        """
        result = await db.exec(
            select(DoctorCategory).where(DoctorCategory.id == category_id)
        )
        return result.first()

    @staticmethod
    async def update(
        slug: str,
        doctor_category_data: DoctorCategoryUpdate,
        db: Session
    ) -> DoctorCategory:
        """
        Update an existing doctor category.

        Args:
            slug (str): The slug of the category to update.
            doctor_category_data (DoctorCategoryUpdate): The data to update.
                Can include title, keywords, and image.
            db (AsyncSession): The database session for executing queries.

        Returns:
            DoctorCategory: The updated doctor category object.

        Raises:
            HTTPException: 404 error if the category is not found.

        Example:
            ```python
            update_data = DoctorCategoryUpdate(
                title="Cardiovascular Medicine",
                keywords=["heart", "cardiovascular", "cardio"]
            )
            updated_category = await DoctorCategoryService.update("cardiology", update_data, db)
            ```
        """
        result = await db.exec(
            select(DoctorCategory).where(DoctorCategory.slug == slug)
        )
        doctor_category = result.one_or_none()
        
        if not doctor_category:
            raise HTTPException(
                status_code=404,
                detail=f"Doctor Category with slug '{slug}' not found"
            )
        
        # Update title and slug
        doctor_category.title = doctor_category_data.title
        doctor_category.slug = slugify(doctor_category_data.title)
        
        # Update optional fields
        if doctor_category_data.keywords is not None:
            doctor_category.keywords = doctor_category_data.keywords
        
        if doctor_category_data.image is not None:
            doctor_category.image = doctor_category_data.image
        
        doctor_category.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(doctor_category)
        
        return doctor_category

    @staticmethod
    async def delete(
        slug: str,
        db: Session
    ) -> DoctorCategory:
        """
        Delete a doctor category by its slug.

        Args:
            slug (str): The slug of the category to delete.
            db (AsyncSession): The database session for executing queries.

        Returns:
            DoctorCategory: The deleted doctor category object (before deletion).

        Raises:
            HTTPException: 404 error if the category is not found.

        Example:
            ```python
            deleted_category = await DoctorCategoryService.delete("cardiology", db)
            print(f"Deleted: {deleted_category.title}")
            ```
        """
        result = await db.exec(
            select(DoctorCategory).where(DoctorCategory.slug == slug)
        )
        doctor_category = result.one_or_none()
        
        if not doctor_category:
            raise HTTPException(
                status_code=404,
                detail=f"Doctor Category with slug '{slug}' not found"
            )
        
        await db.delete(doctor_category)
        await db.commit()
        
        return doctor_category

    @staticmethod
    async def exists_by_slug(
        slug: str,
        db: Session
    ) -> bool:
        """
        Check if a doctor category exists by its slug.

        Args:
            slug (str): The slug to check.
            db (AsyncSession): The database session for executing queries.

        Returns:
            bool: True if the category exists, False otherwise.

        Example:
            ```python
            if await DoctorCategoryService.exists_by_slug("cardiology", db):
                print("Category exists!")
            ```
        """
        result = await db.exec(
            select(DoctorCategory.id).where(DoctorCategory.slug == slug)
        )
        return result.first() is not None

    @staticmethod
    async def search_by_keyword(
        keyword: str,
        db: Session
    ) -> Sequence[DoctorCategory]:
        """
        Search doctor categories by keyword in title or keywords field.

        Args:
            keyword (str): The keyword to search for.
            db (AsyncSession): The database session for executing queries.

        Returns:
            list[DoctorCategory]: A list of matching doctor categories.

        Example:
            ```python
            results = await DoctorCategoryService.search_by_keyword("heart", db)
            for category in results:
                print(category.title)
            ```
        """
        result = await db.exec(
            select(DoctorCategory).where(

                or_(
                    col(DoctorCategory.title).ilike(keyword),
                    col(DoctorCategory.keywords).ilike(keyword),
                )
            )
        )
        return result.all()