"""Authentication API routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserRegisterSchema, UserLoginSchema, UserResponseSchema
from ..services.user_service import UserService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponseSchema)
async def register(
    user_data: UserRegisterSchema,
    db: Session = Depends(get_db),
):
    """Register a new user"""
    user, token = UserService.register_user(
        db, user_data.email, user_data.password, user_data.password_confirm
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
        },
    }


@router.post("/login", response_model=UserResponseSchema)
async def login(
    credentials: UserLoginSchema,
    db: Session = Depends(get_db),
):
    """Login user"""
    user, token = UserService.authenticate_user(db, credentials.email, credentials.password)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
        },
    }
