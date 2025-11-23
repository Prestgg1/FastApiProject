from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Type

from sqlalchemy import Column, DateTime
from sqlmodel import Enum as SQLEnum
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc),
    )


class GenderEnum(str, Enum):
    male = "male"
    female = "female"


gender_enum = SQLEnum(GenderEnum, name="genderenum")


class GenderMixin(SQLModel):
    gender: GenderEnum = Field(sa_column=Column(gender_enum, nullable=False))


class ModelType(str, Enum):
    doctor = "doctor"
    pharmacy = "pharmacy"
    clinic = "clinic"


from .appointment import Appointment
from .basket import Basket
from .blog import Blog
from .brunch import Brunch
from .chat import AIChat, AIChatMessage, Chat, ChatMessage
from .clinic import Clinic
from .customer import Customer
from .doctor import Doctor
from .doctor_category import DoctorCategory
from .favorite import Favorite
from .notification import Notification
from .pharmacy import Pharmacy
from .product import Product
from .product_transaction import ProductTransaction
from .refresh_token import RefreshToken
from .review import Review
from .user import User
