"""Unit tests for Task and TaskList models."""

import pytest
from src.models import Task, TaskList
from src.errors import InvalidTaskError, TaskNotFoundError


class TestTask:
    """Tests for Task model."""

    def test_task_creation(self):
        """Test creating a valid task."""
        task = Task(1, "Buy milk")
        assert task.id == 1
        assert task.description == "Buy milk"
        assert task.completed is False
        assert task.created_at is not None

    def test_task_empty_description_raises_error(self):
        """Test that empty description raises InvalidTaskError."""
        with pytest.raises(InvalidTaskError):
            Task(1, "")

    def test_task_whitespace_description_raises_error(self):
        """Test that whitespace-only description raises InvalidTaskError."""
        with pytest.raises(InvalidTaskError):
            Task(1, "   ")

    def test_task_long_description_raises_error(self):
        """Test that description over 1000 chars raises InvalidTaskError."""
        with pytest.raises(InvalidTaskError):
            Task(1, "a" * 1001)

    def test_task_max_length_description(self):
        """Test that description with exactly 1000 chars is accepted."""
        task = Task(1, "a" * 1000)
        assert len(task.description) == 1000

    def test_task_update_description(self):
        """Test updating task description."""
        task = Task(1, "Buy milk")
        task.update_description("Buy organic milk")
        assert task.description == "Buy organic milk"
        assert task.updated_at is not None

    def test_task_mark_complete(self):
        """Test marking task as complete."""
        task = Task(1, "Buy milk")
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True
        assert task.updated_at is not None

    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(1, "Buy milk", completed=False)
        task_dict = task.to_dict()
        assert task_dict["id"] == 1
        assert task_dict["description"] == "Buy milk"
        assert task_dict["completed"] is False
        assert "created_at" in task_dict

    def test_task_from_dict(self):
        """Test creating task from dictionary."""
        data = {
            "id": 1,
            "description": "Buy milk",
            "completed": False,
            "created_at": "2025-12-29T10:00:00Z",
            "updated_at": None
        }
        task = Task.from_dict(data)
        assert task.id == 1
        assert task.description == "Buy milk"
        assert task.completed is False


class TestTaskList:
    """Tests for TaskList model."""

    def test_create_empty_task_list(self):
        """Test creating an empty task list."""
        task_list = TaskList.create_empty()
        assert task_list.version == 1
        assert task_list.next_id == 1
        assert len(task_list.tasks) == 0

    def test_add_task(self):
        """Test adding a task to the list."""
        task_list = TaskList.create_empty()
        task = task_list.add_task("Buy milk")
        assert task.id == 1
        assert task.description == "Buy milk"
        assert len(task_list.tasks) == 1
        assert task_list.next_id == 2

    def test_add_multiple_tasks(self):
        """Test adding multiple tasks."""
        task_list = TaskList.create_empty()
        task1 = task_list.add_task("Task 1")
        task2 = task_list.add_task("Task 2")
        assert task1.id == 1
        assert task2.id == 2
        assert task_list.next_id == 3
        assert len(task_list.tasks) == 2

    def test_add_task_with_invalid_description_raises_error(self):
        """Test that adding task with invalid description raises error."""
        task_list = TaskList.create_empty()
        with pytest.raises(InvalidTaskError):
            task_list.add_task("")

    def test_find_task(self):
        """Test finding a task by ID."""
        task_list = TaskList.create_empty()
        task_list.add_task("Buy milk")
        found_task = task_list.find_task(1)
        assert found_task.description == "Buy milk"

    def test_find_task_not_found_raises_error(self):
        """Test that finding non-existent task raises TaskNotFoundError."""
        task_list = TaskList.create_empty()
        with pytest.raises(TaskNotFoundError):
            task_list.find_task(999)

    def test_get_all_tasks(self):
        """Test getting all tasks."""
        task_list = TaskList.create_empty()
        task_list.add_task("Task 1")
        task_list.add_task("Task 2")
        tasks = task_list.get_all_tasks()
        assert len(tasks) == 2

    def test_remove_task(self):
        """Test removing a task."""
        task_list = TaskList.create_empty()
        task_list.add_task("Task 1")
        task_list.remove_task(1)
        assert len(task_list.tasks) == 0

    def test_remove_task_not_found_raises_error(self):
        """Test that removing non-existent task raises error."""
        task_list = TaskList.create_empty()
        with pytest.raises(TaskNotFoundError):
            task_list.remove_task(999)

    def test_task_id_never_reused(self):
        """Test that deleted task IDs are never reused."""
        task_list = TaskList.create_empty()
        task1 = task_list.add_task("Task 1")
        task2 = task_list.add_task("Task 2")

        # Delete first task
        task_list.remove_task(1)

        # Add new task - should get ID 3, not 1
        task3 = task_list.add_task("Task 3")
        assert task3.id == 3
        assert task_list.next_id == 4

    def test_to_dict(self):
        """Test converting task list to dictionary."""
        task_list = TaskList.create_empty()
        task_list.add_task("Task 1")
        data = task_list.to_dict()
        assert data["version"] == 1
        assert data["next_id"] == 2
        assert len(data["tasks"]) == 1

    def test_from_dict(self):
        """Test creating task list from dictionary."""
        data = {
            "version": 1,
            "next_id": 3,
            "tasks": [
                {
                    "id": 1,
                    "description": "Task 1",
                    "completed": False,
                    "created_at": "2025-12-29T10:00:00Z",
                    "updated_at": None
                }
            ]
        }
        task_list = TaskList.from_dict(data)
        assert task_list.version == 1
        assert task_list.next_id == 3
        assert len(task_list.tasks) == 1
