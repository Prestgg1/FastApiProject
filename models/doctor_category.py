from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin

if TYPE_CHECKING:
    from models import Doctor


class DoctorCategory(TimestampMixin, SQLModel, table=True):
    __tablename__ = "doctor_categories"  # type:ignore[misc]
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    slug: str = Field(unique=True, index=True, max_length=255)
    keywords: Optional[str] = Field(default=None, max_length=255)
    image: Optional[str] = Field(default=None, max_length=255)
    doctor: list["Doctor"] = Relationship(back_populates="doctor_category")
