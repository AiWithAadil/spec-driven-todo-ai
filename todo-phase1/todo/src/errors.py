"""Custom exceptions for Todo application."""


class TodoError(Exception):
    """Base exception for all Todo application errors."""
    pass


class TaskNotFoundError(TodoError):
    """Raised when a task with the specified ID is not found."""
    pass


class InvalidTaskError(TodoError):
    """Raised when task data is invalid (empty description, etc.)."""
    pass


class StorageError(TodoError):
    """Raised when file I/O operations fail."""
    pass


class CommandError(TodoError):
    """Raised when command arguments are invalid."""
    pass
