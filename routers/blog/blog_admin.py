from fastapi import APIRouter, Depends, status

from database import Session
from dependencies.auth import require_admin
from schemas import BlogCreate, BlogResponse, BlogUpdate
from services.blog_service import BlogService

blog_admin_router = APIRouter(
    prefix="/admin/blogs",
    tags=["Blogs - Admin"],
    dependencies=[Depends(require_admin)],
)


@blog_admin_router.post(
    "/", response_model=BlogResponse, status_code=status.HTTP_201_CREATED
)
async def create_blog(blog: BlogCreate, db: Session):
    return await BlogService.create_blog(db, blog)


@blog_admin_router.patch("/{slug}", response_model=BlogResponse)
async def update_blog(slug: str, blog: BlogUpdate, db: Session):
    return await BlogService.update_blog(db, slug, blog)


@blog_admin_router.delete("/{slug}", status_code=status.HTTP_200_OK)
async def delete_blog(slug: str, db: Session):
    return await BlogService.delete_blog(db, slug)
