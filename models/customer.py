from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import GenderMixin, TimestampMixin

if TYPE_CHECKING:
    from models import Appointment, Favorite, User


class Customer(TimestampMixin, GenderMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="customer")
    favorite: List["Favorite"] = Relationship(back_populates="customer")
    appointment: List["Appointment"] = Relationship(back_populates="customer")
    finCode: str
    phone: str
    birthday: Optional[datetime] = None
    city: str
    region: str
    street: str
    address: str
