from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import ModelType, TimestampMixin

if TYPE_CHECKING:
    from models import Customer


class Favorite(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    model_type: ModelType
    model_id: int
    customer_id: int = Field(foreign_key="customer.id")
    customer: "Customer" = Relationship(back_populates="favorite")
