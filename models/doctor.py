from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column
from sqlmodel import Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel

from models import GenderMixin, TimestampMixin
from models.doctor_category import DoctorCategory
from models.user import User

from . import GenderEnum

if TYPE_CHECKING:
    from models import Review


class Doctor(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="doctor")
    finCode: str = Field(default=None, max_length=7, unique=True)
    phone: str = Field(default=None, max_length=50, unique=True)
    birthday: date = Field(default=None)
    city: str = Field(default=None, max_length=255)
    state: str = Field(default=None, max_length=255)
    country: str = Field(default=None, max_length=255)
    address: str = Field(default=None, max_length=255)
    clinic: str = Field(default=None, max_length=100)
    about: str = Field(default=None, max_length=255)
    gender: GenderEnum = Field(sa_column=Column(SQLEnum(GenderEnum), nullable=False))
    doctor_category_id: int = Field(foreign_key="doctor_categories.id")
    doctor_category: DoctorCategory = Relationship(back_populates="doctor")
    #
    # reviews: List["Review"] = Relationship(
    #     sa_relationship_kwargs={
    #         "primaryjoin": lambda: "and_(foreign(Review.model_id)==Doctor.id, Review.model_type=='doctor')",
    #         "viewonly": True,
    #     }
    # )

    deleted_at: Optional[datetime] = Field(default=None)
