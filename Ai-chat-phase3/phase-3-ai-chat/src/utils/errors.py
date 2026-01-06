"""Error handling and translation for chatbot operations."""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCategory(str, Enum):
    """Error categories for user-friendly translation."""
    DATABASE = "database"
    TOOL = "tool"
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"
    AUTHENTICATION = "authentication"


class ChatbotError(Exception):
    """Base exception for chatbot operations."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.category = category
        self.user_message = user_message or self._default_user_message()
        self.context = context or {}
        super().__init__(self.message)

    def _default_user_message(self) -> str:
        """Generate default user-friendly message."""
        messages = {
            ErrorCategory.DATABASE: "I'm having trouble accessing the database. Please try again.",
            ErrorCategory.TOOL: "I encountered an error while processing your request. Please try again.",
            ErrorCategory.VALIDATION: "I didn't understand your request. Please try again.",
            ErrorCategory.TIMEOUT: "I'm taking longer than usual. Please try again.",
            ErrorCategory.AUTHENTICATION: "You don't have permission to access this resource.",
            ErrorCategory.UNKNOWN: "Something went wrong. Please try again.",
        }
        return messages.get(self.category, messages[ErrorCategory.UNKNOWN])


class DatabaseError(ChatbotError):
    """Database operation error."""

    def __init__(
        self,
        message: str,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            user_message=user_message,
            context=context,
        )


class ToolError(ChatbotError):
    """MCP tool invocation error."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        ctx = context or {}
        if tool_name:
            ctx["tool_name"] = tool_name
        super().__init__(
            message,
            category=ErrorCategory.TOOL,
            user_message=user_message,
            context=ctx,
        )


class ValidationError(ChatbotError):
    """Validation error for input."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        ctx = context or {}
        if field:
            ctx["field"] = field
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            user_message=user_message,
            context=ctx,
        )


class TimeoutError(ChatbotError):
    """Timeout error for operations."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        ctx = context or {}
        if operation:
            ctx["operation"] = operation
        super().__init__(
            message,
            category=ErrorCategory.TIMEOUT,
            user_message=user_message,
            context=ctx,
        )


class AuthenticationError(ChatbotError):
    """Authentication error."""

    def __init__(
        self,
        message: str,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            category=ErrorCategory.AUTHENTICATION,
            user_message=user_message,
            context=context,
        )


def translate_error(error: Exception) -> ChatbotError:
    """Translate generic exceptions to chatbot-specific errors."""
    if isinstance(error, ChatbotError):
        return error

    error_str = str(error).lower()

    if "database" in error_str or "connection" in error_str:
        return DatabaseError(str(error))
    elif "timeout" in error_str:
        return TimeoutError(str(error))
    elif "validation" in error_str:
        return ValidationError(str(error))

    return ChatbotError(str(error))
