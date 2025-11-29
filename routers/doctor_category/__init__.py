from fastapi import APIRouter

from .doctor_category_admin import doctor_category_admin
from .doctor_category_user import doctor_category_user

router = APIRouter()
router.include_router(doctor_category_user)
router.include_router(doctor_category_admin)
