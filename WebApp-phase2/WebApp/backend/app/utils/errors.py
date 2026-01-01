"""Custom exception classes"""
from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    """Raised when login credentials are invalid"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


class DuplicateEmailException(HTTPException):
    """Raised when email is already registered"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )


class InvalidTokenException(HTTPException):
    """Raised when JWT token is invalid or expired"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TaskNotFound(HTTPException):
    """Raised when task is not found"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )


class TaskNotOwnedByUser(HTTPException):
    """Raised when user tries to access task they don't own"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task",
        )


class ValidationException(HTTPException):
    """Raised for validation errors"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
