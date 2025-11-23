from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin

if TYPE_CHECKING:
    from models import Product, Review, User


class Pharmacy(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    user: "User" = Relationship(back_populates="pharmacy")

    slug: Optional[str] = Field(default=None, max_length=255, unique=True)
    about: Optional[str] = Field(default=None, max_length=255)

    address: str = Field(max_length=255)
    city: str = Field(max_length=255)
    state: str = Field(max_length=255)
    country: str = Field(max_length=255)
    product: List["Product"] = Relationship(back_populates="pharmacy")
    # reviews: List["Review"] = Relationship(
    #     back_populates="pharmacy",
    #     sa_relationship_kwargs={
    #         "primaryjoin": "and_(foreign(Review.model_id)==Pharmacy.id, Review.model_type=='pharmacy')",
    #         "viewonly": True,
    #     },
    # )
