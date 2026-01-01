"""Task service for business logic"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import Task, User
from ..utils.errors import TaskNotFound, TaskNotOwnedByUser, ValidationException


class TaskService:
    """Service for task-related operations"""

    @staticmethod
    def get_user_tasks(db: Session, user_id: int) -> list[Task]:
        """Get all tasks for a user, ordered by creation date (newest first)"""
        tasks = db.query(Task).filter(
            Task.user_id == user_id
        ).order_by(desc(Task.created_at)).all()
        return tasks

    @staticmethod
    def create_task(db: Session, user_id: int, title: str, description: str = "") -> Task:
        """Create a new task"""
        # Validate title
        if not title or not title.strip():
            raise ValidationException("Title cannot be empty")

        if len(title) > 255:
            raise ValidationException("Title cannot exceed 255 characters")

        task = Task(user_id=user_id, title=title, description=description)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_task(db: Session, task_id: int, user_id: int) -> Task:
        """Get a specific task, verifying ownership"""
        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            raise TaskNotFound()

        if task.user_id != user_id:
            raise TaskNotOwnedByUser()

        return task

    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        user_id: int,
        title: str | None = None,
        description: str | None = None,
        is_completed: bool | None = None,
    ) -> Task:
        """Update a task"""
        task = TaskService.get_task(db, task_id, user_id)

        if title is not None:
            if not title or not title.strip():
                raise ValidationException("Title cannot be empty")
            if len(title) > 255:
                raise ValidationException("Title cannot exceed 255 characters")
            task.title = title

        if description is not None:
            task.description = description

        if is_completed is not None:
            task.is_completed = is_completed

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int, user_id: int) -> None:
        """Delete a task"""
        task = TaskService.get_task(db, task_id, user_id)
        db.delete(task)
        db.commit()
