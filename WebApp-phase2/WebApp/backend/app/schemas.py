"""Pydantic schemas for request/response validation"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserSchema(BaseModel):
    """Base user schema"""
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserRegisterSchema(BaseModel):
    """Schema for user registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str


class UserLoginSchema(BaseModel):
    """Schema for user login request"""
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    """Schema for authentication response"""
    access_token: str
    token_type: str = "bearer"
    user: UserSchema


# Task Schemas
class TaskSchema(BaseModel):
    """Base task schema"""
    id: int
    user_id: int
    title: str
    description: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskCreateSchema(BaseModel):
    """Schema for task creation"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=10000)


class TaskUpdateSchema(BaseModel):
    """Schema for task update"""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=10000)
    is_completed: bool | None = None


class TaskListSchema(BaseModel):
    """Schema for task list response"""
    tasks: list[TaskSchema]
    total: int
