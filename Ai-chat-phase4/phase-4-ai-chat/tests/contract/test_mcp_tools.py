"""Contract tests for MCP tools."""

import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.todo_manager import TodoManager
from src.models.database import Todo, TodoStatus, TodoPriority
from src.utils.errors import ValidationError


class TestCreateTodoContract:
    """Contract tests for create_todo MCP tool."""

    @pytest.mark.asyncio
    async def test_create_todo_success(self, async_session: AsyncSession, test_user_id: str):
        """Test successful todo creation."""
        manager = TodoManager(async_session)

        todo = await manager.create_todo(
            user_id=test_user_id,
            title="Buy groceries",
            description="Milk, eggs, bread",
            priority=TodoPriority.MEDIUM,
        )

        assert todo is not None
        assert todo.id is not None
        assert todo.title == "Buy groceries"
        assert todo.description == "Milk, eggs, bread"
        assert todo.status == TodoStatus.OPEN
        assert todo.priority == TodoPriority.MEDIUM
        assert todo.user_id == test_user_id
        assert todo.created_at is not None

    @pytest.mark.asyncio
    async def test_create_todo_title_required(self, async_session: AsyncSession, test_user_id: str):
        """Test that title is required."""
        manager = TodoManager(async_session)

        with pytest.raises(ValidationError) as exc_info:
            await manager.create_todo(
                user_id=test_user_id,
                title="",
            )
        assert "Title cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_todo_priority_enum(self, async_session: AsyncSession, test_user_id: str):
        """Test priority enum validation."""
        manager = TodoManager(async_session)

        # Valid priorities
        for priority in [TodoPriority.LOW, TodoPriority.MEDIUM, TodoPriority.HIGH]:
            todo = await manager.create_todo(
                user_id=test_user_id,
                title=f"Todo {priority}",
                priority=priority,
            )
            assert todo.priority == priority

    @pytest.mark.asyncio
    async def test_create_todo_response_schema(self, async_session: AsyncSession, test_user_id: str):
        """Test response schema matches contract."""
        manager = TodoManager(async_session)

        todo = await manager.create_todo(
            user_id=test_user_id,
            title="Test todo",
            description="Test description",
            priority=TodoPriority.HIGH,
        )

        # Validate schema
        assert hasattr(todo, "success") or todo is not None
        assert todo.id
        assert todo.title == "Test todo"
        assert todo.description == "Test description"
        assert todo.status == TodoStatus.OPEN
        assert todo.priority == TodoPriority.HIGH
        assert todo.created_at
        assert todo.updated_at


class TestReadTodosContract:
    """Contract tests for read_todos MCP tool."""

    @pytest.mark.asyncio
    async def test_read_todos_empty_list(self, async_session: AsyncSession, test_user_id: str):
        """Test reading todos when none exist."""
        manager = TodoManager(async_session)
        todos = await manager.read_all(user_id=test_user_id)
        assert todos == []

    @pytest.mark.asyncio
    async def test_read_todos_returns_list(self, async_session: AsyncSession, test_user_id: str):
        """Test read_todos returns array of todos."""
        manager = TodoManager(async_session)

        # Create 2 todos
        await manager.create_todo(user_id=test_user_id, title="Todo 1")
        await manager.create_todo(user_id=test_user_id, title="Todo 2")

        todos = await manager.read_all(user_id=test_user_id)

        assert isinstance(todos, list)
        assert len(todos) == 2
        assert all(isinstance(t, Todo) for t in todos)

    @pytest.mark.asyncio
    async def test_read_todos_excludes_archived(self, async_session: AsyncSession, test_user_id: str):
        """Test that archived todos are excluded by default."""
        manager = TodoManager(async_session)

        todo1 = await manager.create_todo(user_id=test_user_id, title="Open todo")
        todo2 = await manager.create_todo(user_id=test_user_id, title="Archived todo")

        # Archive todo2
        await manager.delete(todo2.id, test_user_id)

        todos = await manager.read_all(user_id=test_user_id)
        assert len(todos) == 1
        assert todos[0].id == todo1.id

    @pytest.mark.asyncio
    async def test_read_todos_response_schema(self, async_session: AsyncSession, test_user_id: str):
        """Test response schema matches contract."""
        manager = TodoManager(async_session)

        await manager.create_todo(user_id=test_user_id, title="Todo 1")
        await manager.create_todo(user_id=test_user_id, title="Todo 2")

        todos = await manager.read_all(user_id=test_user_id)

        assert isinstance(todos, list)
        assert len(todos) == 2
        for todo in todos:
            assert todo.id
            assert todo.title
            assert todo.status in [TodoStatus.OPEN, TodoStatus.COMPLETED, TodoStatus.ARCHIVED]
            assert todo.priority in [TodoPriority.LOW, TodoPriority.MEDIUM, TodoPriority.HIGH]
            assert todo.created_at
            assert todo.updated_at


class TestUpdateTodoContract:
    """Contract tests for update_todo MCP tool."""

    @pytest.mark.asyncio
    async def test_update_todo_success(self, async_session: AsyncSession, test_user_id: str):
        """Test successful todo update."""
        manager = TodoManager(async_session)

        original = await manager.create_todo(user_id=test_user_id, title="Original")
        updated = await manager.update(
            todo_id=original.id,
            user_id=test_user_id,
            title="Updated",
            status=TodoStatus.COMPLETED,
        )

        assert updated.id == original.id
        assert updated.title == "Updated"
        assert updated.status == TodoStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_update_todo_id_required(self, async_session: AsyncSession, test_user_id: str):
        """Test that todo ID is required."""
        manager = TodoManager(async_session)

        with pytest.raises(ValidationError):
            await manager.update(
                todo_id=uuid4(),  # Non-existent
                user_id=test_user_id,
                title="Updated",
            )

    @pytest.mark.asyncio
    async def test_update_todo_optional_fields(self, async_session: AsyncSession, test_user_id: str):
        """Test that update fields are optional."""
        manager = TodoManager(async_session)

        original = await manager.create_todo(
            user_id=test_user_id,
            title="Test",
            description="Test desc",
            priority=TodoPriority.MEDIUM,
        )

        # Update only title
        updated = await manager.update(
            todo_id=original.id,
            user_id=test_user_id,
            title="New title",
        )

        assert updated.title == "New title"
        assert updated.description == "Test desc"  # Unchanged
        assert updated.priority == TodoPriority.MEDIUM  # Unchanged

    @pytest.mark.asyncio
    async def test_update_todo_response_schema(self, async_session: AsyncSession, test_user_id: str):
        """Test response schema matches contract."""
        manager = TodoManager(async_session)

        original = await manager.create_todo(user_id=test_user_id, title="Test")
        updated = await manager.update(
            todo_id=original.id,
            user_id=test_user_id,
            status=TodoStatus.COMPLETED,
        )

        assert updated.id
        assert updated.title
        assert updated.status == TodoStatus.COMPLETED
        assert updated.priority
        assert updated.updated_at


class TestDeleteTodoContract:
    """Contract tests for delete_todo MCP tool."""

    @pytest.mark.asyncio
    async def test_delete_todo_success(self, async_session: AsyncSession, test_user_id: str):
        """Test successful todo deletion (soft-delete)."""
        manager = TodoManager(async_session)

        todo = await manager.create_todo(user_id=test_user_id, title="To delete")
        success = await manager.delete(todo.id, test_user_id)

        assert success is True

        # Verify soft-delete (archived)
        deleted_todo = await manager.read_one(todo.id, test_user_id)
        assert deleted_todo.status == TodoStatus.ARCHIVED

    @pytest.mark.asyncio
    async def test_delete_todo_id_required(self, async_session: AsyncSession, test_user_id: str):
        """Test that todo ID is required."""
        manager = TodoManager(async_session)

        with pytest.raises(ValidationError):
            await manager.delete(uuid4(), test_user_id)  # Non-existent

    @pytest.mark.asyncio
    async def test_delete_todo_not_found(self, async_session: AsyncSession, test_user_id: str):
        """Test deletion of non-existent todo."""
        manager = TodoManager(async_session)

        with pytest.raises(ValidationError) as exc_info:
            await manager.delete(uuid4(), test_user_id)
        assert "Todo not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_todo_response_schema(self, async_session: AsyncSession, test_user_id: str):
        """Test response schema matches contract."""
        manager = TodoManager(async_session)

        todo = await manager.create_todo(user_id=test_user_id, title="To delete")
        success = await manager.delete(todo.id, test_user_id)

        assert isinstance(success, bool)
        assert success is True
