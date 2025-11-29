from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.doctor_schema import DoctorCategoryList


class AppointmentBase(BaseModel):
    full_name: str
    phone: str
    fin_code: str
    complaint: str
    date: datetime
    created_at: datetime
    model_type: str


class AppointmentsDoctorResponse(BaseModel):
    id: int
    appointment_id: int
    clinic: Optional[str] = None
    user: UserField
    doctor_category: DoctorCategoryList
    has_favorited: bool
    average_rating: float
    date: datetime


class AppointmentCreate(BaseModel):
    full_name: str
    phone: str
    fin_code: str
    complaint: str
    date: datetime


class AppointmentUpdate(AppointmentBase):
    full_name: str
    phone: str
    fin_code: str
    complaint: str
    date: datetime


class AppointmentInDB(AppointmentBase):
    id: int
    created_at: datetime
    updated_at: datetime


class AppointmentCustomerResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    image: str
    fin_code: str
    complaint: str
    date: datetime
