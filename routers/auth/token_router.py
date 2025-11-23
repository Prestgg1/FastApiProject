from fastapi import APIRouter, Depends

from database import Session
from dependencies.auth import get_current_user

token_router = APIRouter(tags=["Token"])


@token_router.get("/me")
async def me(db: Session, user=Depends(get_current_user)):
    return user
