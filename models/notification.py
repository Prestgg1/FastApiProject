from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin
from models.user import User


class Notification(TimestampMixin, SQLModel, table=True):
    __tablename__ = "notifications"  # type:ignore[misc]
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: str = Field(max_length=200)
    content: Optional[str] = Field(default=None, max_length=255)
    image: Optional[str] = Field(default=None, max_length=200)
    path: str = Field(max_length=200)

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="notifications")

    is_read: bool = Field(default=False)
