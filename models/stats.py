from typing import Optional

from sqlmodel import Field, SQLModel

from models import ModelType, TimestampMixin


class Stats(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    model_type: ModelType
    model_id: int
    average_rating: float = 0.0
    total_reviews: int = 0
    work_experience: int = 0
    patient_count: int = 0
