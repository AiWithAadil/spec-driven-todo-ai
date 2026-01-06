"""Todo CRUD operations service."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.database import Todo, TodoStatus, TodoPriority
from src.utils.errors import DatabaseError, ValidationError


class TodoManager:
    """Manages todo CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_todo(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: TodoPriority = TodoPriority.MEDIUM,
        created_in_conversation_id: Optional[UUID] = None,
    ) -> Todo:
        """
        Create a new todo (T073: transaction safety).

        Ensures rollback on failure to prevent partial state in database.
        """
        try:
            if not title or not title.strip():
                raise ValidationError(
                    "Title cannot be empty",
                    field="title",
                    user_message="Todo title is required",
                )

            now = datetime.utcnow()
            todo = Todo(
                user_id=user_id,
                title=title.strip(),
                description=description.strip() if description else None,
                priority=priority,
                status=TodoStatus.OPEN,
                created_in_conversation_id=created_in_conversation_id,
                created_at=now,
                updated_at=now,
            )

            self.session.add(todo)
            await self.session.commit()
            await self.session.refresh(todo)
            return todo

        except ValidationError:
            raise
        except Exception as e:
            # T073: Rollback transaction on failure
            await self.session.rollback()
            raise DatabaseError(
                f"Failed to create todo: {str(e)}",
                user_message="I couldn't create the todo. Please try again.",
                context={"error": str(e), "user_id": user_id},
            )

    async def read_all(
        self,
        user_id: str,
        status_filter: Optional[TodoStatus] = None,
    ) -> List[Todo]:
        """
        Read all todos for a user (T064: multi-user isolation).

        Filters todos by user_id to ensure users only see their own todos.
        """
        try:
            query = select(Todo).where(Todo.user_id == user_id)

            if status_filter:
                query = query.where(Todo.status == status_filter)
            else:
                # Default: exclude archived
                query = query.where(Todo.status != TodoStatus.ARCHIVED)

            query = query.order_by(Todo.updated_at.desc())
            result = await self.session.execute(query)
            return result.scalars().all()

        except Exception as e:
            raise DatabaseError(
                f"Failed to read todos: {str(e)}",
                user_message="I couldn't retrieve your todos. Please try again.",
                context={"error": str(e), "user_id": user_id},
            )

    async def read_one(self, todo_id: UUID, user_id: str) -> Optional[Todo]:
        """
        Read a single todo by ID (T064: multi-user isolation).

        Filters by both todo_id and user_id to ensure users can only access their own todos.
        """
        try:
            query = select(Todo).where(
                and_(
                    Todo.id == todo_id,
                    Todo.user_id == user_id,
                )
            )
            result = await self.session.execute(query)
            return result.scalars().first()

        except Exception as e:
            raise DatabaseError(
                f"Failed to read todo: {str(e)}",
                user_message="I couldn't retrieve the todo. Please try again.",
                context={"error": str(e), "todo_id": str(todo_id), "user_id": user_id},
            )

    async def update(
        self,
        todo_id: UUID,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TodoStatus] = None,
        priority: Optional[TodoPriority] = None,
    ) -> Optional[Todo]:
        """Update a todo."""
        try:
            # Get existing todo
            todo = await self.read_one(todo_id, user_id)
            if not todo:
                raise ValidationError(
                    f"Todo not found: {todo_id}",
                    field="todo_id",
                    user_message="I couldn't find that todo.",
                )

            # Update fields
            if title is not None:
                if not title.strip():
                    raise ValidationError(
                        "Title cannot be empty",
                        field="title",
                        user_message="Todo title cannot be empty.",
                    )
                todo.title = title.strip()

            if description is not None:
                todo.description = description.strip() if description else None

            if status is not None:
                todo.status = status

            if priority is not None:
                todo.priority = priority

            todo.updated_at = datetime.utcnow()

            self.session.add(todo)
            await self.session.commit()
            await self.session.refresh(todo)
            return todo

        except ValidationError:
            raise
        except Exception as e:
            await self.session.rollback()
            raise DatabaseError(
                f"Failed to update todo: {str(e)}",
                user_message="I couldn't update the todo. Please try again.",
                context={"error": str(e), "todo_id": str(todo_id), "user_id": user_id},
            )

    async def delete(self, todo_id: UUID, user_id: str) -> bool:
        """Delete (soft-delete) a todo."""
        try:
            todo = await self.read_one(todo_id, user_id)
            if not todo:
                raise ValidationError(
                    f"Todo not found: {todo_id}",
                    field="todo_id",
                    user_message="I couldn't find that todo.",
                )

            # Soft delete
            todo.status = TodoStatus.ARCHIVED
            todo.updated_at = datetime.utcnow()

            self.session.add(todo)
            await self.session.commit()
            return True

        except ValidationError:
            raise
        except Exception as e:
            await self.session.rollback()
            raise DatabaseError(
                f"Failed to delete todo: {str(e)}",
                user_message="I couldn't delete the todo. Please try again.",
                context={"error": str(e), "todo_id": str(todo_id), "user_id": user_id},
            )

    async def get_audit_trail(self, message_id: UUID) -> List:
        """Get all tool invocations for a message."""
        try:
            from src.models.database import ToolInvocation

            query = select(ToolInvocation).where(
                ToolInvocation.message_id == message_id
            ).order_by(ToolInvocation.timestamp.asc())

            result = await self.session.execute(query)
            return result.scalars().all()

        except Exception as e:
            raise DatabaseError(
                f"Failed to retrieve audit trail: {str(e)}",
                context={"error": str(e), "message_id": str(message_id)},
            )
