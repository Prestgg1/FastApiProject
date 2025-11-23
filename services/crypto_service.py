import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from database import Session
from models.refresh_token import RefreshToken

# Config
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

password_hasher = PasswordHash.recommended()


class CryptoService:
    """Crypto və Auth utility funksiyaları"""

    # ------------------------
    # Password Hashing
    # ------------------------
    @staticmethod
    def hash_password(password: str) -> str:
        """Şifrə hashing"""
        return password_hasher.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Şifrə doğrulama"""
        return password_hasher.verify(password, hashed)

    # ------------------------
    # Access Token
    # ------------------------
    @staticmethod
    def create_access_token(data: dict) -> str:
        """Access token (qısa ömürlü)"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # ------------------------
    # Refresh Token
    # ------------------------
    @staticmethod
    async def create_refresh_token(user_id: int, db: Session, device_id: str) -> str:
        """
        Yeni refresh token yarat, hash-lə DB-də saxla.
        Rotation üçün hər dəfə token yenilənir.
        """
        # Token üçün random string
        raw_token = secrets.token_urlsafe(64)
        hashed_token = password_hasher.hash(raw_token)

        # Expiration
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )

        # DB insert
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=hashed_token,
            device_id=device_id,
            expires_at=expires_at,
        )

        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
        return raw_token

    # ------------------------
    # Token decode / verify
    # ------------------------
    @staticmethod
    def decode_token(token: str) -> dict:
        """Token decode + validity yoxlama"""
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    @staticmethod
    async def verify_refresh_token(
        raw_token: str, user_id: int, db: AsyncSession
    ) -> RefreshToken | None:
        """
        Refresh token-i DB-də verify et:
        - Token istifadəçi üçün mövcuddurmu
        - Token expired və ya revoked deyil
        - Hash-lə raw token match edir
        """
        # Bütün refresh token-ləri istifadəçi üzrə götür
        statement = select(RefreshToken).where(RefreshToken.user_id == user_id)
        result = await db.exec(statement)
        tokens = result.all()

        # Token-ləri yoxla
        for token in tokens:
            if token.is_revoked or token.expires_at < datetime.utcnow():
                continue
            if password_hasher.verify(raw_token, token.token_hash):
                return token

        return None
