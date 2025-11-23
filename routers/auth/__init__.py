from fastapi import APIRouter

from .authorization import auth_router
from .token_router import token_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(token_router)
