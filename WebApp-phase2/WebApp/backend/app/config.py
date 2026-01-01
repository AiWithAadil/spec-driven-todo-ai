"""Application configuration from environment variables"""
import os
from typing import List


class Settings:
    """Application settings loaded from environment variables"""

    def __init__(self):
        # Database - SQLite by default
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "sqlite:///./todo_app.db"
        )

        # JWT
        self.secret_key: str = os.getenv(
            "SECRET_KEY",
            "your-secret-key-change-in-production"
        )
        self.algorithm: str = "HS256"
        self.access_token_expire_hours: int = 7 * 24  # 7 days

        # CORS
        cors_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
        self.cors_origins: List[str] = [c.strip() for c in cors_str.split(",")]

        # API
        self.api_title: str = "Todo App API"
        self.api_version: str = "1.0.0"
        self.debug: bool = os.getenv("DEBUG", "True").lower() == "true"


settings = Settings()
