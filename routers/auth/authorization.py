from fastapi import APIRouter, Depends, Header
from sqlmodel.ext.asyncio.session import AsyncSession

from database import Session, get_db
from schemas.user_schema import AuthResponse, CustomerRegister, UserLogin
from services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", response_model=AuthResponse)
async def login(user_data: UserLogin, db: Session, x_device_id: str = Header(...)):
    return await AuthService.login(user_data, db, x_device_id)


@auth_router.post("/register", response_model=AuthResponse)
async def register_customer(
    user_data: CustomerRegister, db: Session, x_device_id: str = Header(...)
):
    return await AuthService.register_customer(user_data, db, x_device_id)
