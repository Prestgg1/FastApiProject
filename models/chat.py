from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin

if TYPE_CHECKING:
    from models import User


class ChatMessageType(str, Enum):
    text = "text"
    image = "image"
    video = "video"


# ---------------- Chat ----------------
class Chat(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user1_id: int = Field(foreign_key="user.id")
    user2_id: int = Field(foreign_key="user.id")
    is_closed: bool = Field(default=False)

    # user1: "User" = Relationship()
    # user2: "User" = Relationship()
    # messages: List["ChatMessage"] = Relationship(back_populates="chat")


# ---------------- AIChat ----------------
class AIChat(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="ai_chat")
    # messages: List["AIChatMessage"] = Relationship(back_populates="chat")


# ---------------- AIChatMessage ----------------
class AIChatMessage(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    chat_id: int = Field(foreign_key="chat.id")
    sender_id: int = Field(foreign_key="user.id")
    message: str
    message_type: ChatMessageType = Field(default=ChatMessageType.text)
    is_read: bool = Field(default=False)

    # chat: "AIChat" = Relationship(back_populates="message")
    # sender: "User" = Relationship()


# ---------------- ChatMessage ----------------
class ChatMessage(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    chat_id: int = Field(foreign_key="chat.id")
    sender_id: int = Field(foreign_key="user.id")
    message: str
    message_type: ChatMessageType = Field(default=ChatMessageType.text)
    is_read: bool = Field(default=False)

    # chat: "Chat" = Relationship(back_populates="message")
    # sender: "User" = Relationship()
