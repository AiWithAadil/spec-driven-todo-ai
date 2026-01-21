"""Pydantic request/response schemas for API."""

from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from src.models.database import TodoStatus, TodoPriority, MessageRole


# ========================
# Request Schemas
# ========================
class ChatRequest(BaseModel):
    """Request to chat endpoint."""

    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID or null for new",
    )
    message: str = Field(
        ...,
        max_length=10000,
        description="User message",
    )


# ========================
# Todo Schemas
# ========================
class TodoSchema(BaseModel):
    """Todo representation."""

    id: UUID
    user_id: str
    title: str
    description: Optional[str] = None
    status: TodoStatus
    priority: TodoPriority
    created_at: datetime
    updated_at: datetime
    created_in_conversation_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class TodoCreateRequest(BaseModel):
    """Request to create a todo."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[TodoPriority] = Field(default=TodoPriority.MEDIUM)


class TodoUpdateRequest(BaseModel):
    """Request to update a todo."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None


# ========================
# Message Schemas
# ========================
class MessageSchema(BaseModel):
    """Message representation."""

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


# ========================
# Tool Invocation Schemas
# ========================
class ToolInvocationSchema(BaseModel):
    """Tool invocation representation."""

    id: UUID
    message_id: UUID
    tool_name: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True


# ========================
# Response Schemas
# ========================
class ChatResponseMetadata(BaseModel):
    """Metadata in chat response."""

    timestamp: datetime
    message_count: int

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z" if v and not v.isoformat().endswith("Z") else v.isoformat() if v else None
        }


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    conversation_id: UUID
    message_id: UUID
    response: str
    todos: List[TodoSchema]
    tool_invocations: List[ToolInvocationSchema]
    metadata: ChatResponseMetadata


class ConversationSchema(BaseModel):
    """Conversation representation."""

    id: UUID
    user_id: str
    created_at: datetime
    last_updated_at: datetime
    messages: Optional[List[MessageSchema]] = None

    class Config:
        from_attributes = True


# ========================
# MCP Tool Response Schemas
# ========================
class MCPToolResponse(BaseModel):
    """Base response from MCP tool."""

    success: bool
    error: Optional[str] = None


class CreateTodoResponse(MCPToolResponse):
    """Response from create_todo MCP tool."""

    todo: Optional[TodoSchema] = None


class ReadTodosResponse(MCPToolResponse):
    """Response from read_todos MCP tool."""

    todos: List[TodoSchema] = []
    count: int = 0


class UpdateTodoResponse(MCPToolResponse):
    """Response from update_todo MCP tool."""

    todo: Optional[TodoSchema] = None


class DeleteTodoResponse(MCPToolResponse):
    """Response from delete_todo MCP tool."""

    deleted_id: Optional[UUID] = None


# ========================
# Error Schemas
# ========================
class ErrorResponse(BaseModel):
    """Error response."""

    status_code: int
    message: str
    request_id: str
    context: Optional[Dict[str, Any]] = None
