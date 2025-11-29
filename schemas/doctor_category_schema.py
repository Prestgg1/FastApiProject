from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DoctorCategoryList(BaseModel):
    id: int
    title: str
    slug: str
    image: str


class DoctorCategoryBase(BaseModel):
    title: str
    keywords: Optional[str] = None
    image: Optional[str] = None
    status: Optional[bool] = True


class DoctorCategoryCreate(DoctorCategoryBase):
    pass


class DoctorCategoryUpdate(DoctorCategoryBase):
    pass


class DoctorCategoryResponse(DoctorCategoryBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
