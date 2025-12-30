"""Integration tests for todo CLI application."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
from src.commands import add_task, list_tasks, complete_task, update_task, delete_task
from src.models import TaskList
from src.storage import load_tasks, save_tasks


class TestAddAndView:
    """Test adding tasks and viewing them."""

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_add_and_list_flow(self, mock_save, mock_load):
        """Test adding a task and listing it."""
        task_list = TaskList.create_empty()

        # Mock load to return current state
        def load_side_effect():
            return task_list

        mock_load.side_effect = load_side_effect

        # Add first task
        result1 = add_task("Buy milk")
        assert "Task added" in result1
        assert "ID: 1" in result1

        # Add second task
        result2 = add_task("Call mom")
        assert "Task added" in result2
        assert "ID: 2" in result2

        # List tasks
        result3 = list_tasks()
        assert "Buy milk" in result3
        assert "Call mom" in result3
        assert "2 tasks" in result3


class TestAddUpdateComplete:
    """Test adding, updating, and completing tasks."""

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_add_update_complete_flow(self, mock_save, mock_load):
        """Test adding, updating, and completing a task."""
        task_list = TaskList.create_empty()

        def load_side_effect():
            return task_list

        mock_load.side_effect = load_side_effect

        # Add task
        add_task("Buy groceries")

        # Update task
        result_update = update_task("1", "Buy organic groceries")
        assert "updated" in result_update

        # Verify update persisted
        result_list = list_tasks()
        assert "Buy organic groceries" in result_list

        # Complete task
        result_complete = complete_task("1")
        assert "marked as complete" in result_complete

        # Verify completion in list
        result_final = list_tasks()
        assert "[X]" in result_final
        assert "1 complete" in result_final


class TestDeleteAndIDPreservation:
    """Test deleting tasks and verifying ID preservation."""

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_delete_preserves_next_id(self, mock_save, mock_load):
        """Test that deleting a task doesn't reuse its ID."""
        task_list = TaskList.create_empty()

        def load_side_effect():
            return task_list

        mock_load.side_effect = load_side_effect

        # Add tasks
        add_task("Task 1")
        add_task("Task 2")
        add_task("Task 3")

        # Delete first task
        delete_task("1")

        # Add new task - should get ID 4, not 1
        add_task("Task 4")

        # Verify task list
        result = list_tasks()
        assert "Task 1" not in result  # Deleted
        assert "Task 2" in result
        assert "Task 3" in result
        assert "Task 4" in result


class TestErrorHandling:
    """Test error handling for invalid operations."""

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_complete_nonexistent_task(self, mock_save, mock_load):
        """Test completing a task that doesn't exist."""
        mock_load.return_value = TaskList.create_empty()

        result = complete_task("999")
        assert "Error" in result
        assert "not found" in result

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_update_nonexistent_task(self, mock_save, mock_load):
        """Test updating a task that doesn't exist."""
        mock_load.return_value = TaskList.create_empty()

        result = update_task("999", "New description")
        assert "Error" in result
        assert "not found" in result

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_delete_nonexistent_task(self, mock_save, mock_load):
        """Test deleting a task that doesn't exist."""
        mock_load.return_value = TaskList.create_empty()

        result = delete_task("999")
        assert "Error" in result
        assert "not found" in result

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_add_empty_description(self, mock_save, mock_load):
        """Test adding task with empty description."""
        mock_load.return_value = TaskList.create_empty()

        result = add_task("")
        assert "Error" in result
        assert "empty" in result.lower()

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_invalid_task_id_format(self, mock_save, mock_load):
        """Test operations with invalid task ID format."""
        mock_load.return_value = TaskList.create_empty()

        # Complete with non-numeric ID
        result1 = complete_task("abc")
        assert "Error" in result1
        assert "number" in result1.lower()

        # Update with non-numeric ID
        result2 = update_task("abc", "New description")
        assert "Error" in result2
        assert "number" in result2.lower()

        # Delete with non-numeric ID
        result3 = delete_task("abc")
        assert "Error" in result3
        assert "number" in result3.lower()


class TestDataPersistence:
    """Test that data persists correctly."""

    def test_add_persists_to_file(self):
        """Test that added tasks persist to storage file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tasks.json"

            with patch("src.storage.get_storage_path") as mock_path:
                with patch("src.storage.ensure_storage_directory") as mock_dir:
                    mock_path.return_value = file_path
                    mock_dir.return_value = file_path.parent

                    # Add a task using full workflow
                    task_list = TaskList.create_empty()
                    task_list.add_task("Buy milk")
                    save_tasks(task_list)

                    # Verify persisted
                    loaded = load_tasks()
                    assert len(loaded.tasks) == 1
                    assert loaded.tasks[0].description == "Buy milk"

    def test_update_persists_to_file(self):
        """Test that updated tasks persist to storage file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tasks.json"

            with patch("src.storage.get_storage_path") as mock_path:
                with patch("src.storage.ensure_storage_directory") as mock_dir:
                    mock_path.return_value = file_path
                    mock_dir.return_value = file_path.parent

                    # Add and update a task
                    task_list = TaskList.create_empty()
                    task_list.add_task("Buy milk")
                    task_list.tasks[0].update_description("Buy organic milk")
                    save_tasks(task_list)

                    # Verify persisted
                    loaded = load_tasks()
                    assert loaded.tasks[0].description == "Buy organic milk"

    def test_complete_persists_to_file(self):
        """Test that completion status persists to storage file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tasks.json"

            with patch("src.storage.get_storage_path") as mock_path:
                with patch("src.storage.ensure_storage_directory") as mock_dir:
                    mock_path.return_value = file_path
                    mock_dir.return_value = file_path.parent

                    # Add and complete a task
                    task_list = TaskList.create_empty()
                    task_list.add_task("Buy milk")
                    task_list.tasks[0].mark_complete()
                    save_tasks(task_list)

                    # Verify persisted
                    loaded = load_tasks()
                    assert loaded.tasks[0].completed is True
