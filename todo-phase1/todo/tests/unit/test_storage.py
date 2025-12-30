"""Unit tests for storage layer."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from src.storage import get_storage_path, load_tasks, save_tasks, ensure_storage_directory, init_if_needed
from src.models import TaskList, Task
from src.errors import StorageError


class TestStoragePath:
    """Tests for storage path functions."""

    def test_get_storage_path(self):
        """Test getting storage path."""
        path = get_storage_path()
        assert isinstance(path, Path)
        assert "tasks.json" in str(path)

    def test_ensure_storage_directory(self):
        """Test ensuring storage directory exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("src.storage.get_storage_path") as mock_path:
                mock_path.return_value = Path(tmpdir) / "todo" / "tasks.json"
                directory = ensure_storage_directory()
                assert directory.exists()


class TestLoadTasks:
    """Tests for load_tasks function."""

    def test_load_empty_when_file_not_exists(self):
        """Test loading tasks when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("src.storage.get_storage_path") as mock_path:
                mock_path.return_value = Path(tmpdir) / "tasks.json"
                task_list = load_tasks()
                assert len(task_list.tasks) == 0
                assert task_list.next_id == 1

    def test_load_existing_tasks(self):
        """Test loading existing tasks from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tasks.json"

            # Create a sample task file
            data = {
                "version": 1,
                "next_id": 2,
                "tasks": [
                    {
                        "id": 1,
                        "description": "Buy milk",
                        "completed": False,
                        "created_at": "2025-12-29T10:00:00Z",
                        "updated_at": None
                    }
                ]
            }

            with open(file_path, "w") as f:
                json.dump(data, f)

            with patch("src.storage.get_storage_path") as mock_path:
                mock_path.return_value = file_path
                task_list = load_tasks()
                assert len(task_list.tasks) == 1
                assert task_list.tasks[0].description == "Buy milk"

    def test_load_invalid_json_raises_error(self):
        """Test that invalid JSON raises StorageError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tasks.json"

            # Create invalid JSON file
            with open(file_path, "w") as f:
                f.write("invalid json {")

            with patch("src.storage.get_storage_path") as mock_path:
                mock_path.return_value = file_path
                with pytest.raises(StorageError):
                    load_tasks()


class TestSaveTasks:
    """Tests for save_tasks function."""

    def test_save_tasks(self):
        """Test saving tasks to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tasks.json"

            with patch("src.storage.get_storage_path") as mock_path:
                with patch("src.storage.ensure_storage_directory") as mock_dir:
                    mock_path.return_value = file_path
                    mock_dir.return_value = file_path.parent

                    task_list = TaskList.create_empty()
                    task_list.add_task("Buy milk")
                    save_tasks(task_list)

                    # Verify file was created
                    assert file_path.exists()

                    # Verify content
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    assert len(data["tasks"]) == 1
                    assert data["tasks"][0]["description"] == "Buy milk"

    def test_save_tasks_creates_temp_file(self):
        """Test that save_tasks creates temp file for atomic writes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tasks.json"
            temp_path = file_path.with_suffix(".tmp")

            with patch("src.storage.get_storage_path") as mock_path:
                with patch("src.storage.ensure_storage_directory") as mock_dir:
                    mock_path.return_value = file_path
                    mock_dir.return_value = file_path.parent

                    task_list = TaskList.create_empty()
                    task_list.add_task("Buy milk")
                    save_tasks(task_list)

                    # Temp file should not remain after save
                    assert not temp_path.exists()
                    # Real file should exist
                    assert file_path.exists()


class TestInitIfNeeded:
    """Tests for init_if_needed function."""

    def test_init_creates_empty_file(self):
        """Test that init_if_needed creates empty file if not exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tasks.json"

            with patch("src.storage.get_storage_path") as mock_path:
                with patch("src.storage.ensure_storage_directory") as mock_dir:
                    mock_path.return_value = file_path
                    mock_dir.return_value = file_path.parent

                    task_list = init_if_needed()

                    # Verify file was created
                    assert file_path.exists()
                    assert len(task_list.tasks) == 0

    def test_init_loads_existing_file(self):
        """Test that init_if_needed loads existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tasks.json"

            # Create existing file
            data = {
                "version": 1,
                "next_id": 2,
                "tasks": [
                    {
                        "id": 1,
                        "description": "Existing task",
                        "completed": False,
                        "created_at": "2025-12-29T10:00:00Z",
                        "updated_at": None
                    }
                ]
            }

            with open(file_path, "w") as f:
                json.dump(data, f)

            with patch("src.storage.get_storage_path") as mock_path:
                with patch("src.storage.ensure_storage_directory") as mock_dir:
                    mock_path.return_value = file_path
                    mock_dir.return_value = file_path.parent

                    task_list = init_if_needed()
                    assert len(task_list.tasks) == 1
                    assert task_list.tasks[0].description == "Existing task"
