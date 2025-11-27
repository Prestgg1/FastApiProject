from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from models import GenderEnum
from schemas.user_schema import UserField


class CustomerBase(BaseModel):
    finCode: str
    phone: str
    gender: GenderEnum
    birthday: date
    city: str
    region: str
    street: str
    address: str


class CustomerCreate(CustomerBase):
    user_id: int  # Required on creation


class CustomerOut(CustomerBase):
    id: int
    user: UserField
    created_at: datetime


class CustomerUpdate(BaseModel):
    finCode: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    city: Optional[str] = None
    region: Optional[str] = None
    street: Optional[str] = None
    address: Optional[str] = None
