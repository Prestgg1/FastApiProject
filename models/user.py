from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin

if TYPE_CHECKING:
    from models import (
        AIChat,
        Basket,
        Brunch,
        Clinic,
        Customer,
        Doctor,
        Notification,
        Pharmacy,
        Review,
    )


class UserRole(PyEnum):
    admin = "admin"
    customer = "customer"
    doctor = "doctor"
    brunch = "brunch"
    clinic = "clinic"
    pharmacy = "pharmacy"


class User(TimestampMixin, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True)
    name: str = Field(max_length=255)
    email: str = Field(max_length=255, unique=True, index=True)
    password: str = Field(max_length=255)
    image: str = Field(
        default="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
        max_length=255,
    )
    customer: Optional["Customer"] = Relationship(back_populates="user")
    doctor: Optional["Doctor"] = Relationship(back_populates="user")
    clinic: Optional["Clinic"] = Relationship(back_populates="user")
    pharmacy: Optional["Pharmacy"] = Relationship(back_populates="user")
    brunch: Optional["Brunch"] = Relationship(back_populates="user")
    status: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.customer)
    review: list["Review"] = Relationship(back_populates="user")
    notifications: list["Notification"] = Relationship(back_populates="user")
    ai_chat: list["AIChat"] = Relationship(back_populates="user")
    basket: list["Basket"] = Relationship(back_populates="user")
