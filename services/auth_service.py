from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from database import Session
from models.user import UserRole
from schemas.user_schema import AuthResponse, CustomerRegister, UserBase, UserLogin
from services.crypto_service import CryptoService
from services.customer_service import CustomerService
from services.user_service import UserService


class AuthService:
    """Authentication service"""

    # ------------------------
    # LOGIN
    # ------------------------
    @staticmethod
    async def login(user_data: UserLogin, db: AsyncSession, device_id: str):
        """User login + token creation"""

        user = await UserService.verify_credentials(
            email=user_data.email, password=user_data.password, db=db
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not user.status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )
        

        access_token = CryptoService.create_access_token({"user_id": user.id})


        refresh_token = await CryptoService.create_refresh_token(
            user_id=user.id, db=db, device_id=device_id
        )

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    # ------------------------
    # REGISTER CUSTOMER
    # ------------------------
    @staticmethod
    async def register_customer(
        user_data: CustomerRegister, db: AsyncSession, device_id: str
    ) -> AuthResponse:
        """
        Customer qeydiyyatı:
        - User + Customer yaradılır
        - Access + Refresh token yaradılır
        """

        # User yarat
        try:
            new_user = await UserService.create(
                email=user_data.email,
                password=user_data.password,
                name=user_data.name,
                role=UserRole.customer,
                db=db,
            )
        except HTTPException as e:
            if e.status_code == status.HTTP_400_BAD_REQUEST:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=[
                        {
                            "loc": ["body", "email"],
                            "msg": "İstifadəçi artıq var",
                            "type": "value_error",
                        }
                    ],
                )
            raise

        # Customer yarat
        try:
            await CustomerService.create(
                user_id=new_user.id,
                fin_code=user_data.finCode,
                phone=user_data.phone,
                gender=user_data.gender,
                birthday=user_data.birthday,
                city=user_data.city,
                region=user_data.region,
                street=user_data.street,
                address=user_data.address,
                db=db,
            )
        except Exception as e:
            await UserService.delete(new_user.id, db)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create customer profile: {str(e)}",
            )

        # Token-lər
        access_token = CryptoService.create_access_token({"user_id": new_user.id})
        refresh_token = await CryptoService.create_refresh_token(
            user_id=new_user.id, db=db, device_id=device_id
        )

        return AuthResponse(
            user=new_user,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    # ------------------------
    # REFRESH TOKEN FLOW
    # ------------------------
    @staticmethod
    async def refresh_tokens(
        user_id: int, raw_refresh_token: str, db: AsyncSession, device_id: str
    ) -> AuthResponse | None:
        """
        Refresh token istifadə edilərək:
        - Köhnə token revoke edilir
        - Yeni access + refresh token yaradılır
        """
        token_obj = await CryptoService.verify_refresh_token(
            raw_refresh_token, user_id=user_id, db=db
        )
        if not token_obj:
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )
        db.add(token_obj)
        await db.commit()

        access_token = CryptoService.create_access_token({"user_id": user_id})
        refresh_token = await CryptoService.create_refresh_token(
            user_id=user_id, db=db, device_id=device_id
        )

        user = await UserService.get_by_id(user_id, db)
        if not user:
            HTTPException(status_code=404, detail="User not found")
            return None

        return AuthResponse(
            user=UserBase(
                id=user.id,
                name=user.name,
                email=user.email,
                image=user.image,
                role=user.role,
                status=user.status,
            ),
            access_token=access_token,
            refresh_token=refresh_token,
        )

