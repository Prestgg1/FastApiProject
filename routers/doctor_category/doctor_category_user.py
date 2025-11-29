"""
Doctor Category User Router

Public endpoints for accessing doctor categories.
No authentication required.
"""

from typing import Sequence
from fastapi import APIRouter, Query

from database import Session
from schemas.doctor_category_schema import (
    DoctorCategoryList,
    DoctorCategoryResponse,
)
from services.doctor_category_service import DoctorCategoryService


doctor_category_user = APIRouter(
    prefix="/doctor_categories",
    tags=["Doctor Categories - Public"],
)


@doctor_category_user.get(
    "/",
    response_model=list[DoctorCategoryList],
    summary="Get all doctor categories (partial data)",
    description="Retrieve a list of all doctor categories with basic information (id, title, slug, image).",
)
async def get_all_categories(db: Session):
    """
    Get all doctor categories with partial data.
    
    Returns only id, title, slug, and image for performance optimization.
    Suitable for listing pages and dropdowns.
    """
    return await DoctorCategoryService.get_all_partial(db)


@doctor_category_user.get(
    "/search",
    response_model=list[DoctorCategoryResponse],
    summary="Search doctor categories",
    description="Search for doctor categories by keyword in title or keywords field.",
)
async def search_categories(
    db: Session,
    keyword: str = Query(..., min_length=2, description="Search keyword"),
):
    """
    Search doctor categories by keyword.
    
    - **keyword**: Search term (minimum 2 characters)
    
    Searches in both title and keywords fields.
    """
    return await DoctorCategoryService.search_by_keyword(keyword, db)


@doctor_category_user.get(
    "/{slug}",
    response_model=DoctorCategoryResponse,
    summary="Get a doctor category by slug",
    description="Retrieve complete information for a specific doctor category.",
)
async def get_category_by_slug(
    slug: str,
    db: Session
):
    """
    Get a specific doctor category by slug.
    
    - **slug**: The unique slug identifier
    
    Returns complete category information including all fields.
    """
    return await DoctorCategoryService.get_by_slug(slug, db)