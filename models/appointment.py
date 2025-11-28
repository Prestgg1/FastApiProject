from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin

if TYPE_CHECKING:
    from models import Customer


class AppointmentStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CancelledBy(str, Enum):
    CUSTOMER = "customer"
    DOCTOR = "doctor"


class Appointment(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    full_name: str
    phone: str
    fin_code: str
    complaint: str
    status: AppointmentStatus = Field(default=AppointmentStatus.PENDING)
    date: datetime
    model_type: str
    model_id: int
    reason: Optional[str] = None
    cancelled_by: Optional[CancelledBy] = None
    customer_id: int = Field(foreign_key="customer.id")
    customer: "Customer" = Relationship(back_populates="appointment")
