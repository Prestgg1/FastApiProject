from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin

if TYPE_CHECKING:
    from models import ProductTransaction, User


class BasketStatus(PyEnum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Basket(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    total_price: float = Field(default=0.0)
    status: BasketStatus = Field(default=BasketStatus.pending)
    product_transactions: list["ProductTransaction"] | None = Relationship(
        back_populates="basket", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    user: "User" = Relationship(back_populates="basket")
