"""
Doctor Category Admin Router

Admin endpoints for managing doctor categories.
Requires admin authentication.
"""

from fastapi import APIRouter, Depends

from database import Session
from dependencies.auth import require_admin
from schemas.doctor_category_schema import (
    DoctorCategoryCreate,
    DoctorCategoryResponse,
    DoctorCategoryUpdate,
)
from services.doctor_category_service import DoctorCategoryService


doctor_category_admin = APIRouter(
    prefix="/admin/doctor_categories",
    tags=["Doctor Categories - Admin"],
    dependencies=[Depends(require_admin)],
)


@doctor_category_admin.post(
    "/",
    response_model=DoctorCategoryResponse,
    summary="Create a new doctor category",
    description="Create a new doctor category with title, keywords, and image.",
)
async def create_category(
    doctor_category: DoctorCategoryCreate,
    db: Session
) :
    """
    Create a new doctor category.
    
    - **title**: Category title (required)
    - **keywords**: List of keywords for search optimization
    - **image**: Image URL or path
    """
    return await DoctorCategoryService.create(doctor_category, db)


@doctor_category_admin.get(
    "/",
    response_model=list[DoctorCategoryResponse],
    summary="Get all doctor categories",
    description="Retrieve a complete list of all doctor categories with full details.",
)
async def get_all_categories(db: Session):
    """Get all doctor categories with complete information."""
    return await DoctorCategoryService.get_all(db)


@doctor_category_admin.get(
    "/{slug}",
    response_model=DoctorCategoryResponse,
    summary="Get a doctor category by slug",
    description="Retrieve a specific doctor category by its slug identifier.",
)
async def get_category_by_slug(
    slug: str,
    db: Session
):
    """
    Get a specific doctor category by slug.
    
    - **slug**: The unique slug identifier
    """
    return await DoctorCategoryService.get_by_slug(slug, db)


@doctor_category_admin.put(
    "/{slug}",
    response_model=DoctorCategoryResponse,
    summary="Update a doctor category",
    description="Update an existing doctor category's information.",
)
async def update_category(
    slug: str,
    doctor_category_data: DoctorCategoryUpdate,
    db: Session,
):
    """
    Update a doctor category.
    
    - **slug**: The slug of the category to update
    - **title**: New title (required)
    - **keywords**: Updated keywords list
    - **image**: Updated image URL
    """
    return await DoctorCategoryService.update(slug, doctor_category_data, db)


@doctor_category_admin.delete(
    "/{slug}",
    response_model=DoctorCategoryResponse,
    summary="Delete a doctor category",
    description="Delete a doctor category by its slug.",
)
async def delete_category(
    slug: str,
    db: Session
):
    """
    Delete a doctor category.
    
    - **slug**: The slug of the category to delete
    
    Returns the deleted category information.
    """
    return await DoctorCategoryService.delete(slug, db)