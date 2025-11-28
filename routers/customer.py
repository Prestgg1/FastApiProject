from typing import List, Sequence

from fastapi import APIRouter, Depends

from database import Session
from dependencies.auth import require_admin
from models import Customer
from schemas.customer_schema import CustomerOut, CustomerUpdate
from services.customer_service import CustomerService

router = APIRouter(
    prefix="/admin/customers",
    tags=["Customers - Admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/")
async def get_all_customers(db: Session)->Sequence[Customer]:
    return await CustomerService.get_all(db)


@router.get("/{customer_id}")
async def get_customer(customer_id: int, db: Session) -> Customer:
    return await CustomerService.get_by_id(customer_id, db)


@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(customer_id: int, customer_data: CustomerUpdate, db: Session):
    return await CustomerService.update(
        customer_id, db, **customer_data.dict(exclude_unset=True)
    )


@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: Session):
    return await CustomerService.delete(customer_id, db)
