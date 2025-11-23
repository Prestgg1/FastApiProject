from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator

from models import GenderEnum
from models.user import UserRole


class UserBase(BaseModel):
    id: int
    name: str
    email: EmailStr
    image: str
    status: bool
    role: UserRole


class CustomerRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    finCode: str
    gender: GenderEnum
    phone: str
    birthday: datetime
    city: str
    region: str
    street: str
    address: str

    @field_validator("finCode")
    def finCode_must_be_7_chars(cls, v):
        if len(v) != 7:
            raise ValueError("Fin kodu 7 simvoldan ibaret olmalı")
        return v

    @field_validator("phone")
    def phone_must_be_12_chars(cls, v):
        if len(v) > 13:
            raise ValueError("Telefon nomresi 12 simvoldan böyük olmamalıdır")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: UserBase
    access_token: str
    refresh_token: str
