from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import User
from models.user import UserRole
from schemas.user_schema import UserBase
from services.crypto_service import CryptoService


class UserService:
    """User CRUD əməliyyatları"""

    @staticmethod
    async def get_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
        """ID-yə görə user tap"""
        return await db.get(User, user_id)

    @staticmethod
    async def get_by_email(email: str, db: AsyncSession) -> Optional[User]:
        """Email-ə görə user tap"""
        result = await db.exec(select(User).where(User.email == email))
        return result.one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
    ) -> Sequence[User]:
        """Bütün user-ləri al"""
        query = select(User).offset(skip).limit(limit)

        if role:
            query = query.where(User.role == role)

        result = await db.exec(query)
        return result.all()

    @staticmethod
    async def create(
        email: str, password: str, name: str, role: UserRole, db: AsyncSession
    ) -> UserBase:
        """Yeni user yarat"""
        # Email-in mövcudluğunu yoxla
        existing_user = await UserService.get_by_email(email, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # User yarat
        new_user = User(
            name=name,
            email=email,
            password=CryptoService.hash_password(password),
            role=role,
            status=True,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserBase(
            name=new_user.name,
            email=new_user.email,
            id=new_user.id,
            image=new_user.image,
            status=new_user.status,
            role=new_user.role,
        )

    @staticmethod
    async def update(user_id: int, db: AsyncSession, **kwargs) -> User:
        """User məlumatlarını yenilə"""
        user = await UserService.get_by_id(user_id, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Password update olunursa hash-lə
        if "password" in kwargs and kwargs["password"]:
            kwargs["password"] = CryptoService.hash_password(kwargs["password"])

        # Update ediləcək field-ləri yenilə
        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def delete(user_id: int, db: AsyncSession) -> bool:
        """User-i sil"""
        user = await UserService.get_by_id(user_id, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await db.delete(user)
        await db.commit()

        return True

    @staticmethod
    async def deactivate(user_id: int, db: AsyncSession) -> User:
        """User-i deaktiv et"""
        return await UserService.update(user_id, db, is_active=False)

    @staticmethod
    async def activate(user_id: int, db: AsyncSession) -> User:
        """User-i aktiv et"""
        return await UserService.update(user_id, db, is_active=True)

    @staticmethod
    async def verify_credentials(
        email: str, password: str, db: AsyncSession
    ) -> Optional[UserBase]:
        """Email və şifrəni yoxla"""
        user = await UserService.get_by_email(email, db)

        if not user:
            print("User not found")
            return None

        if not CryptoService.verify_password(password, user.password):
            print("Password not match")
            return None
        print("User verified")

        return UserBase(
            name=user.name,
            email=user.email,
            id=user.id,
            image=user.image,
            status=user.status,
            role=user.role,
        )
