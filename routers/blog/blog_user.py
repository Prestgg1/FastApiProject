from fastapi import APIRouter, Depends, Query

from database import Session
from schemas import BlogResponse
from services.blog_service import BlogService

blog_user_router = APIRouter(prefix="/blogs", tags=["Blogs - User"])


@blog_user_router.get("/", response_model=list[BlogResponse])
async def get_all_blogs(
    db: Session,
    skip: int = Query(0, ge=0, description="Neçə blog keç"),
    limit: int = Query(100, ge=1, le=100, description="Maksimum blog sayı"),
):
    """Bütün blogları gətir (public)"""
    return await BlogService.get_all_blogs(db, skip, limit)


@blog_user_router.get("/search", response_model=list[BlogResponse])
async def search_blogs(
    db: Session,
    q: str = Query(..., min_length=2, description="Axtarış sorğusu"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Blog axtar (public)"""
    return await BlogService.search_blogs(db, q, skip, limit)


@blog_user_router.get("/{slug}", response_model=BlogResponse)
async def get_blog(slug: str, db: Session):
    """Tək blog gətir (public)"""
    return await BlogService.get_blog(db, slug)
