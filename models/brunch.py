from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin

if TYPE_CHECKING:
    from models import Clinic, User


class Brunch(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    user_id: int = Field(foreign_key="user.id")
    clinic_id: Optional[int] = Field(default=None, foreign_key="clinic.id")

    user: "User" = Relationship(back_populates="brunch")
    clinic: "Clinic" = Relationship(back_populates="brunch")

    location: str
    slug: Optional[str] = None
    image: Optional[str] = None
    average_rating: float = 0
    deleted: bool = False
