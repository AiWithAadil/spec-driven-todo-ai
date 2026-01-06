"""SQLModel database schema definitions."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship, Column, String, DateTime, Enum as SqlEnum
from sqlalchemy import UniqueConstraint, Index, Uuid, func, text


class TodoStatus(str, Enum):
    """Todo status enumeration."""
    OPEN = "open"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TodoPriority(str, Enum):
    """Todo priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"


# ========================
# Conversation Model
# ========================
class Conversation(SQLModel, table=True):
    """Represents a single chat session."""

    id: Optional[UUID] = Field(default=None, primary_key=True, sa_type=Uuid)
    user_id: str = Field(index=True, sa_type=String(255))
    created_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))
    last_updated_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = uuid4()
        super().__init__(**data)

    class Config:
        table_args = (
            Index("idx_user_created", "user_id", "created_at"),
        )


# ========================
# Message Model
# ========================
class Message(SQLModel, table=True):
    """Represents a single message in conversation."""

    id: Optional[UUID] = Field(default=None, primary_key=True, sa_type=Uuid)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True, sa_type=Uuid)
    role: MessageRole = Field(sa_type=SqlEnum(MessageRole))
    content: str = Field(max_length=10000)
    timestamp: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    tool_invocations: List["ToolInvocation"] = Relationship(
        back_populates="message",
        cascade_delete=True,
    )

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = uuid4()
        super().__init__(**data)

    class Config:
        table_args = (
            Index("idx_conversation_timestamp", "conversation_id", "timestamp"),
        )


# ========================
# Todo Model
# ========================
class Todo(SQLModel, table=True):
    """Represents a user's todo item."""

    id: Optional[UUID] = Field(default=None, primary_key=True, sa_type=Uuid)
    user_id: str = Field(index=True, sa_type=String(255))
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: TodoStatus = Field(default=TodoStatus.OPEN, sa_type=SqlEnum(TodoStatus))
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM, sa_type=SqlEnum(TodoPriority))
    created_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))
    updated_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))
    created_in_conversation_id: Optional[UUID] = Field(
        default=None,
        foreign_key="conversation.id",
        index=True,
        sa_type=Uuid,
    )

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = uuid4()
        super().__init__(**data)

    class Config:
        table_args = (
            Index("idx_user_status_updated", "user_id", "status", "updated_at"),
            Index("idx_user_conversation", "user_id", "created_in_conversation_id"),
        )


# ========================
# ToolInvocation Model
# ========================
class ToolInvocation(SQLModel, table=True):
    """Represents a single MCP tool invocation (audit log)."""

    id: Optional[UUID] = Field(default=None, primary_key=True, sa_type=Uuid)
    message_id: UUID = Field(foreign_key="message.id", index=True, sa_type=Uuid)
    tool_name: str = Field(max_length=100)
    parameters: dict = Field(sa_type=String)  # JSON string
    result: dict = Field(sa_type=String)  # JSON string
    status: str = Field(max_length=20)  # "success" or "failure"
    timestamp: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))

    # Relationships
    message: Message = Relationship(back_populates="tool_invocations")

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = uuid4()
        super().__init__(**data)

    class Config:
        table_args = (
            Index("idx_message_timestamp", "message_id", "timestamp"),
            Index("idx_tool_timestamp", "tool_name", "timestamp"),
        )
