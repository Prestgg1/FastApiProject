from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from database import Session
from models.user import User, UserRole
from services.crypto_service import CryptoService
from services.user_service import UserService

security = HTTPBearer()


async def get_current_user(
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


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.customer: #TODO: Change this to admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu əməliyyat üçün admin hüququ lazımdır",
        )
    return current_user


async def get_optional_user(
    db: Session,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[User]:


    if not credentials or not credentials.credentials:
        return None
    result = CryptoService.decode_token(credentials.credentials)
    if not result:
        return None
    return await UserService.get_by_id(result["user_id"], db)
