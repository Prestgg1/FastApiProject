from fastapi import APIRouter

from . import auth, blog, customer, doctor_category, mail

api_router = APIRouter(prefix="/api")

api_router.include_router(blog.router)
api_router.include_router(doctor_category.router)
api_router.include_router(auth.router)
api_router.include_router(customer.router)
api_router.include_router(mail.router)
