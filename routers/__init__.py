from fastapi import APIRouter

from . import auth, blog, customer

api_router = APIRouter(prefix="/api")

api_router.include_router(blog.router)
api_router.include_router(auth.router)
api_router.include_router(customer.router)
