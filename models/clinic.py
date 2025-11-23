from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin

if TYPE_CHECKING:
    from models import Brunch, Review, User


class Clinic(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="clinic")

    about: Optional[str] = None
    address: str
    phone: Optional[str] = None
    city: str
    state: str
    country: str
    brunch: List["Brunch"] = Relationship(back_populates="clinic")
    deleted_at: Optional[datetime] = None

    # brunches: List["Brunch"] = Relationship(back_populates="clinic")
    # reviews: List["Review"] = Relationship(
    #     sa_relationship_kwargs={
    #         "primaryjoin": "and_(foreign(Review.model_id)==Clinic.id, Review.model_type=='clinic')",
    #         "viewonly": True,
    #     }
    # )
