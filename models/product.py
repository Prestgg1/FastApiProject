from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin

if TYPE_CHECKING:
    from models import Pharmacy, ProductTransaction, Review


class Product(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    pharmacy_id: int = Field(foreign_key="pharmacy.id")
    name: str = Field(max_length=255)
    stock: int = Field(default=0)
    price: float
    image: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pharmacy: "Pharmacy" = Relationship(back_populates="product")
    product_stats: Optional["ProductStats"] = Relationship(
        back_populates="product", sa_relationship_kwargs={"uselist": False}
    )
    product_transactions: list["ProductTransaction"] = Relationship(
        back_populates="product"
    )


class ProductStats(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    product_id: int = Field(foreign_key="product.id")

    views: int = Field(default=0)
    average_rating: float = Field(default=0.0)
    reviews_count: int = Field(default=0)
    purchases: int = Field(default=0)
    product: "Product" = Relationship(back_populates="product_stats")
