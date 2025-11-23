from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin

if TYPE_CHECKING:
    from models import Basket, Product


class ProductTransaction(TimestampMixin, SQLModel, table=True):
    __tablename__ = "product_transactions"  # type:ignore[misc]
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    basket_id: int = Field(foreign_key="basket.id")
    basket: Optional["Basket"] = Relationship(back_populates="product_transactions")
    product_id: int = Field(foreign_key="product.id")
    product: "Product" = Relationship(back_populates="product_transactions")
    quantity: int
    price: float
