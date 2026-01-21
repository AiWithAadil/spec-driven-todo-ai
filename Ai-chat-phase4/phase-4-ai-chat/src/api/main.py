"""FastAPI application setup and initialization."""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connection import init_db, close_db, get_session
from src.utils.logging import get_logger, set_request_id, LogEndpointMetrics
from src.utils.errors import ChatbotError
from src.models.schemas import ErrorResponse

# Initialize logger
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    logger.info("Starting application...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    try:
        await close_db()
        logger.info("Database closed successfully")
    except Exception as e:
        logger.error("Failed to close database", error=str(e))


# Create FastAPI app
app = FastAPI(
    title="AI-Powered Todo Chatbot",
    description="Manage todos through natural language conversation",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================
# Request Context Middleware
# ========================
@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Add request ID to context."""
    request_id = request.headers.get("X-Request-ID")
    if request_id:
        set_request_id(request_id)
    else:
        set_request_id(None)  # Will generate new one in logger

    response = await call_next(request)
    return response


# ========================
# Exception Handlers
# ========================
@app.exception_handler(ChatbotError)
async def chatbot_error_handler(request: Request, exc: ChatbotError):
    """Handle ChatbotError exceptions."""
    logger.error(
        "ChatbotError occurred",
        error_category=exc.category.value,
        error_message=exc.message,
        context=exc.context,
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status_code": status.HTTP_400_BAD_REQUEST,
            "message": exc.user_message,
            "request_id": request.headers.get("X-Request-ID", "unknown"),
            "context": exc.context,
        },
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        "Unexpected error",
        error_type=type(exc).__name__,
        error_message=str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "An unexpected error occurred. Please try again.",
            "request_id": request.headers.get("X-Request-ID", "unknown"),
        },
    )


# ========================
# Health Check
# ========================
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


# ========================
# Routes
# ========================
# Import routes after app is created to avoid circular imports
from src.api.routes.chat import router as chat_router

app.include_router(chat_router, prefix="/chat", tags=["chat"])


# ========================
# Root Endpoint
# ========================
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": "AI-Powered Todo Chatbot",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "chat": "/chat/messages",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
