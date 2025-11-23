from fastapi import APIRouter

from .blog_admin import blog_admin_router
from .blog_user import blog_user_router

router = APIRouter()

router.include_router(blog_user_router)
router.include_router(blog_admin_router)
