from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Column, Field, Relationship, SQLModel, Text

from models import TimestampMixin

if TYPE_CHECKING:
    from models import User


class Review(TimestampMixin, SQLModel, table=True):
    __tablename__ = "reviews"  # type:ignore[misc]
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    review: str = Field(sa_column=Column(Text, nullable=False))
    rating: Optional[int] = Field(default=None)
    model_type: str = Field(max_length=50)
    model_id: int
    user_id: int = Field(foreign_key="user.id")
    deleted_at: Optional[datetime] = Field(default=None)
    user: "User" = Relationship(sa_relationship=relationship(back_populates="review"))
