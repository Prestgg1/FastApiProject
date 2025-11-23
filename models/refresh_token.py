from datetime import datetime

from sqlmodel import Field, SQLModel

from models import TimestampMixin


class RefreshToken(TimestampMixin, SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token_hash: str
    device_id: str
    expires_at: datetime
    is_revoked: bool = Field(default=False)
