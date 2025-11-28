from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from database import Session
from models.user import User
from services.crypto_service import CryptoService
from services.user_service import UserService

security = HTTPBearer()


async def only_doctor(
    db: Session,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User | None:
    token = credentials.credentials
    result = CryptoService.decode_token(token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    user = await UserService.get_by_id(result["user_id"], db)
    return user


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu əməliyyat üçün admin hüququ lazımdır",
        )
    return current_user
