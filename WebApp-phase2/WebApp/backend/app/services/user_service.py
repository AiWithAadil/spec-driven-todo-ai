"""User service for authentication logic"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import User
from ..utils.security import hash_password, verify_password, create_access_token
from ..utils.errors import InvalidCredentialsException, DuplicateEmailException, ValidationException


class UserService:
    """Service for user-related operations"""

    @staticmethod
    def register_user(db: Session, email: str, password: str, password_confirm: str) -> tuple[User, str]:
        """Register a new user"""
        # Validate passwords match
        if password != password_confirm:
            raise ValidationException("Passwords do not match")

        # Validate password length
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters")

        # Check for existing email
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise DuplicateEmailException()

        # Create new user
        hashed_password = hash_password(password)
        user = User(email=email, hashed_password=hashed_password)

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            raise DuplicateEmailException()

        # Generate token
        # Note: JWT 'sub' claim must be a string
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

        return user, access_token

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> tuple[User, str]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        # Generate token
        # Note: JWT 'sub' claim must be a string
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

        return user, access_token
