from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BlogCreate(BaseModel):
    """Blog yaratmaq üçün"""

    title: str = Field(..., min_length=1, max_length=255, description="Blog başlığı")
    description: str = Field(
        ..., min_length=1, max_length=255, description="Qısa təsvir"
    )
    text: str = Field(..., min_length=1, description="Blog məzmunu")
    keywords: Optional[str] = Field(None, max_length=255, description="Açar sözlər")
    image: Optional[str] = Field(None, max_length=255, description="Şəkil URL-i")
    status: bool = Field(default=True, description="Yayımlanıb/Draft")
    slug: Optional[str] = Field(
        None,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL slug (avtomatik yaranır)",
    )

    @field_validator("title", "description", "text")
    @classmethod
    def validate_not_empty(cls, v: str, info) -> str:
        """Boş string yoxlamaq"""
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} boş ola bilməz")
        return v.strip()

    @field_validator("keywords", "image")
    @classmethod
    def validate_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        """Optional string-ləri təmizlə"""
        if v is not None:
            v = v.strip()
            return v if v else None
        return None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Slug formatını yoxla"""
        if v is not None:
            v = v.strip().lower()
            if v and not v.replace("-", "").replace("_", "").isalnum():
                raise ValueError("Slug yalnız hərflər, rəqəmlər və defis ola bilər")
            return v if v else None
        return None


class BlogUpdate(BaseModel):
    """Blog yeniləmək üçün (partial)"""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Blog başlığı"
    )
    description: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Qısa təsvir"
    )
    text: Optional[str] = Field(None, min_length=1, description="Blog məzmunu")
    keywords: Optional[str] = Field(None, max_length=255, description="Açar sözlər")
    image: Optional[str] = Field(None, max_length=255, description="Şəkil URL-i")
    status: Optional[bool] = Field(None, description="Yayımlanıb/Draft")

    @field_validator("title", "description", "text")
    @classmethod
    def validate_not_empty(cls, v: Optional[str], info) -> Optional[str]:
        """Boş string yoxlamaq"""
        if v is not None:
            if not v.strip():
                raise ValueError(f"{info.field_name} boş ola bilməz")
            return v.strip()
        return None

    @field_validator("keywords", "image")
    @classmethod
    def validate_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        """Optional string-ləri təmizlə"""
        if v is not None:
            v = v.strip()
            return v if v else None
        return None


class BlogResponse(BaseModel):
    """API response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    description: str
    text: str
    keywords: Optional[str] = None
    image: Optional[str] = None
    status: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
