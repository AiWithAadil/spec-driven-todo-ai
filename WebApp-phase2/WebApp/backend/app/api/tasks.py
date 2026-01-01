"""Task API routes"""
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import TaskSchema, TaskCreateSchema, TaskUpdateSchema, TaskListSchema
from ..services.task_service import TaskService
from ..dependencies import get_current_user
from ..utils.security import decode_token
from ..utils.errors import InvalidTokenException

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


async def get_current_user_from_auth(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Extract current user from Authorization header"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"[AUTH] Received Authorization header: {bool(authorization)}")

    if not authorization:
        logger.error("[AUTH] No Authorization header provided")
        raise InvalidTokenException()

    if not authorization.startswith("Bearer "):
        logger.error(f"[AUTH] Invalid Authorization header format: {authorization[:20]}")
        raise InvalidTokenException()

    try:
        token = authorization.split(" ", 1)[1]
        logger.info(f"[AUTH] Extracted token: {token[:20]}...")
    except IndexError:
        logger.error("[AUTH] Failed to extract token from Authorization header")
        raise InvalidTokenException()

    payload = decode_token(token)
    user_id_str = payload.get("sub")
    logger.info(f"[AUTH] Decoded user_id from token: {user_id_str}")

    if not user_id_str:
        logger.error("[AUTH] No user_id in token payload")
        raise InvalidTokenException()

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        logger.error(f"[AUTH] Invalid user_id format: {user_id_str}")
        raise InvalidTokenException()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"[AUTH] User not found with id: {user_id}")
        raise InvalidTokenException()

    logger.info(f"[AUTH] Successfully authenticated user: {user.email}")
    return user


@router.get("", response_model=TaskListSchema)
async def list_tasks(
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Get all tasks for current user"""
    tasks = TaskService.get_user_tasks(db, current_user.id)
    return {
        "tasks": [
            {
                "id": t.id,
                "user_id": t.user_id,
                "title": t.title,
                "description": t.description,
                "is_completed": t.is_completed,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
            }
            for t in tasks
        ],
        "total": len(tasks),
    }


@router.post("", response_model=TaskSchema)
async def create_task(
    task_data: TaskCreateSchema,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Create a new task"""
    task = TaskService.create_task(
        db, current_user.id, task_data.title, task_data.description
    )
    return {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Get a specific task"""
    task = TaskService.get_task(db, task_id, current_user.id)
    return {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int,
    task_data: TaskUpdateSchema,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Update a task"""
    task = TaskService.update_task(
        db,
        task_id,
        current_user.id,
        task_data.title,
        task_data.description,
        task_data.is_completed,
    )
    return {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.patch("/{task_id}", response_model=TaskSchema)
async def partial_update_task(
    task_id: int,
    task_data: TaskUpdateSchema,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Partial update of a task (e.g., toggle completion)"""
    task = TaskService.update_task(
        db,
        task_id,
        current_user.id,
        task_data.title,
        task_data.description,
        task_data.is_completed,
    )
    return {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Delete a task"""
    TaskService.delete_task(db, task_id, current_user.id)
    return None
