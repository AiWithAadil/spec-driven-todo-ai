"""Unit tests for command implementations."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.commands import add_task, list_tasks, complete_task, update_task, delete_task, help_command
from src.models import TaskList


class TestAddTaskCommand:
    """Tests for add_task command."""

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_add_task_success(self, mock_save, mock_load):
        """Test successfully adding a task."""
        mock_load.return_value = TaskList.create_empty()
        result = add_task("Buy milk")
        assert "Task added" in result
        assert "ID: 1" in result
        mock_save.assert_called_once()

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_add_task_empty_description(self, mock_save, mock_load):
        """Test adding task with empty description."""
        mock_load.return_value = TaskList.create_empty()
        result = add_task("")
        assert "Error" in result
        assert "empty" in result.lower()

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_add_task_long_description(self, mock_save, mock_load):
        """Test adding task with description too long."""
        mock_load.return_value = TaskList.create_empty()
        result = add_task("a" * 1001)
        assert "Error" in result
        assert "exceed" in result.lower()


class TestListTasksCommand:
    """Tests for list_tasks command."""

    @patch("src.commands.load_tasks")
    def test_list_tasks_empty(self, mock_load):
        """Test listing tasks when none exist."""
        mock_load.return_value = TaskList.create_empty()
        result = list_tasks()
        assert "No tasks found" in result

    @patch("src.commands.load_tasks")
    def test_list_tasks_with_tasks(self, mock_load):
        """Test listing tasks when tasks exist."""
        task_list = TaskList.create_empty()
        task_list.add_task("Buy milk")
        task_list.add_task("Call mom")
        mock_load.return_value = task_list
        result = list_tasks()
        assert "Buy milk" in result
        assert "Call mom" in result
        assert "2 tasks" in result


class TestCompleteTaskCommand:
    """Tests for complete_task command."""

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_complete_task_success(self, mock_save, mock_load):
        """Test successfully completing a task."""
        task_list = TaskList.create_empty()
        task_list.add_task("Buy milk")
        mock_load.return_value = task_list
        result = complete_task("1")
        assert "marked as complete" in result
        mock_save.assert_called_once()

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_complete_task_not_found(self, mock_save, mock_load):
        """Test completing non-existent task."""
        mock_load.return_value = TaskList.create_empty()
        result = complete_task("999")
        assert "Error" in result
        assert "not found" in result

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_complete_task_invalid_id(self, mock_save, mock_load):
        """Test completing task with invalid ID."""
        mock_load.return_value = TaskList.create_empty()
        result = complete_task("abc")
        assert "Error" in result
        assert "number" in result.lower()

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_complete_task_already_complete(self, mock_save, mock_load):
        """Test marking already-complete task (idempotent)."""
        task_list = TaskList.create_empty()
        task = task_list.add_task("Buy milk")
        task.mark_complete()
        mock_load.return_value = task_list
        result = complete_task("1")
        assert "marked as complete" in result


class TestUpdateTaskCommand:
    """Tests for update_task command."""

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_update_task_success(self, mock_save, mock_load):
        """Test successfully updating a task."""
        task_list = TaskList.create_empty()
        task_list.add_task("Buy milk")
        mock_load.return_value = task_list
        result = update_task("1", "Buy organic milk")
        assert "updated" in result
        mock_save.assert_called_once()

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_update_task_not_found(self, mock_save, mock_load):
        """Test updating non-existent task."""
        mock_load.return_value = TaskList.create_empty()
        result = update_task("999", "New description")
        assert "Error" in result
        assert "not found" in result

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_update_task_empty_description(self, mock_save, mock_load):
        """Test updating task with empty description."""
        task_list = TaskList.create_empty()
        task_list.add_task("Buy milk")
        mock_load.return_value = task_list
        result = update_task("1", "")
        assert "Error" in result
        assert "empty" in result.lower()


class TestDeleteTaskCommand:
    """Tests for delete_task command."""

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_delete_task_success(self, mock_save, mock_load):
        """Test successfully deleting a task."""
        task_list = TaskList.create_empty()
        task_list.add_task("Buy milk")
        mock_load.return_value = task_list
        result = delete_task("1")
        assert "deleted" in result
        mock_save.assert_called_once()

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_delete_task_not_found(self, mock_save, mock_load):
        """Test deleting non-existent task."""
        mock_load.return_value = TaskList.create_empty()
        result = delete_task("999")
        assert "Error" in result
        assert "not found" in result

    @patch("src.commands.load_tasks")
    @patch("src.commands.save_tasks")
    def test_delete_task_invalid_id(self, mock_save, mock_load):
        """Test deleting task with invalid ID."""
        mock_load.return_value = TaskList.create_empty()
        result = delete_task("abc")
        assert "Error" in result
        assert "number" in result.lower()


class TestHelpCommand:
    """Tests for help_command."""

    def test_help_command_general(self):
        """Test general help command."""
        result = help_command()
        assert "Usage:" in result
        assert "add" in result
        assert "list" in result

    def test_help_command_specific(self):
        """Test help for specific command."""
        result = help_command("add")
        assert "add" in result.lower()

    def test_help_command_unknown(self):
        """Test help for unknown command."""
        result = help_command("unknown")
        assert "Unknown" in result
