from datetime import datetime
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Customer, GenderEnum, User
from models.user import UserRole
from schemas.user_schema import CustomerRegister


class CustomerService:
    """Customer CRUD əməliyyatları"""

    @staticmethod
    async def get_by_id(customer_id: int, db: AsyncSession) -> Optional[Customer]:
        """ID-yə görə customer tap"""
        return await db.get(Customer, customer_id)

    @staticmethod
    async def get_by_user_id(user_id: int, db: AsyncSession) -> Optional[Customer]:
        """User ID-yə görə customer tap"""
        result = await db.exec(select(Customer).where(Customer.user_id == user_id))
        return result.first()

    @staticmethod
    async def get_by_fin_code(fin_code: str, db: AsyncSession) -> Optional[Customer]:
        """FIN kod-a görə customer tap"""
        result = await db.exec(select(Customer).where(Customer.finCode == fin_code))
        return result.first()

    @staticmethod
    async def get_all(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[Customer]:
        """Bütün customer-ləri al"""
        result = await db.exec(select(Customer).offset(skip).limit(limit))
        return result.all()

    @staticmethod
    async def create(
        user_id: int,
        fin_code: str,
        phone: str,
        db: AsyncSession,
        gender: GenderEnum,
        birthday: datetime,
        city: str,
        region: str,
        street: str,
        address: str,
    ) -> Customer:
        """Yeni customer yarat"""
        # FIN code-un mövcudluğunu yoxla
        existing_customer = await CustomerService.get_by_fin_code(fin_code, db)
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FIN code already registered",
            )

        # User-in mövcudluğunu və customer-ə çevrilə biləcəyini yoxla
        existing_user_customer = await CustomerService.get_by_user_id(user_id, db)
        if existing_user_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has a customer profile",
            )

        # Customer yarat
        new_customer = Customer(
            user_id=user_id,
            finCode=fin_code,
            phone=phone,
            gender=gender,
            birthday=birthday,
            city=city,
            region=region,
            street=street,
            address=address,
        )

        db.add(new_customer)
        await db.commit()
        await db.refresh(new_customer)

        return new_customer

    @staticmethod
    async def update(customer_id: int, db: AsyncSession, **kwargs) -> Customer:
        """Customer məlumatlarını yenilə"""
        customer = await CustomerService.get_by_id(customer_id, db)

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
            )

        # Update ediləcək field-ləri yenilə
        for key, value in kwargs.items():
            if value is not None and hasattr(customer, key):
                setattr(customer, key, value)

        db.add(customer)
        await db.commit()
        await db.refresh(customer)

        return customer

    @staticmethod
    async def delete(customer_id: int, db: AsyncSession) -> bool:
        """Customer-i sil"""
        customer = await CustomerService.get_by_id(customer_id, db)

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
            )

        await db.delete(customer)
        await db.commit()

        return True

    @staticmethod
    async def get_with_user(customer_id: int, db: AsyncSession) -> Optional[Customer]:
        """Customer-i User məlumatı ilə birlikdə al"""
        result = await db.exec(select(Customer).where(Customer.id == customer_id))
        customer = result.first()

        if customer:
            await db.refresh(customer, ["user"])

        return customer
