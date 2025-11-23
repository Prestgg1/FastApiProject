from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel, Text

from models import TimestampMixin


class Blog(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    slug: str = Field(unique=True, index=True, max_length=255)
    description: str = Field(max_length=255)
    text: str = Field(sa_column=Column(Text, nullable=False))
    keywords: Optional[str] = Field(default=None, max_length=255)
    image: Optional[str] = Field(default=None, max_length=255)
    status: bool = Field(default=True)
