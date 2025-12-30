"""File persistence layer for tasks."""

import json
import os
from pathlib import Path
from typing import Optional
from src.models import TaskList
from src.errors import StorageError


def get_storage_path() -> Path:
    """Get the storage file path (cross-platform).

    Returns:
        Path to tasks.json file

    Raises:
        StorageError: If path cannot be determined
    """
    try:
        # Use ~/.todo/tasks.json on Unix/macOS
        # Use %USERPROFILE%\.todo\tasks.json on Windows
        home = Path.home()
        todo_dir = home / ".todo"
        return todo_dir / "tasks.json"
    except Exception as e:
        raise StorageError(f"Cannot determine storage path: {e}")


def ensure_storage_directory() -> Path:
    """Ensure the storage directory exists.

    Returns:
        Path to the storage directory

    Raises:
        StorageError: If directory cannot be created
    """
    try:
        storage_path = get_storage_path()
        storage_dir = storage_path.parent

        # Create directory if it doesn't exist
        storage_dir.mkdir(parents=True, exist_ok=True)

        return storage_dir
    except Exception as e:
        raise StorageError(f"Cannot create storage directory: {e}")


def load_tasks() -> TaskList:
    """Load tasks from JSON file.

    Returns:
        TaskList with loaded tasks

    Raises:
        StorageError: If file cannot be read or JSON is invalid
    """
    try:
        storage_path = get_storage_path()

        # If file doesn't exist, return empty task list
        if not storage_path.exists():
            return TaskList.create_empty()

        # Read and parse JSON file
        with open(storage_path, "r") as f:
            data = json.load(f)

        # Deserialize into TaskList
        task_list = TaskList.from_dict(data)
        return task_list

    except json.JSONDecodeError as e:
        raise StorageError(f"Invalid JSON in task file: {e}")
    except IOError as e:
        raise StorageError(f"Cannot read task file: {e}")
    except Exception as e:
        raise StorageError(f"Error loading tasks: {e}")


def save_tasks(task_list: TaskList) -> None:
    """Save tasks to JSON file with atomic writes.

    Args:
        task_list: TaskList to save

    Raises:
        StorageError: If file cannot be written
    """
    try:
        # Ensure directory exists
        ensure_storage_directory()

        storage_path = get_storage_path()
        temp_path = storage_path.with_suffix(".tmp")

        # Convert to dictionary
        data = task_list.to_dict()

        # Write to temporary file first (atomic write)
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)

        # Rename temporary file to actual file (atomic on most systems)
        # On Windows, we need to remove the target first if it exists
        if os.name == "nt" and storage_path.exists():
            storage_path.unlink()

        temp_path.replace(storage_path)

    except IOError as e:
        raise StorageError(f"Cannot write task file: {e}")
    except Exception as e:
        raise StorageError(f"Error saving tasks: {e}")


def init_if_needed() -> TaskList:
    """Initialize storage with empty task list if needed.

    Returns:
        Loaded or newly created TaskList

    Raises:
        StorageError: If initialization fails
    """
    try:
        ensure_storage_directory()

        storage_path = get_storage_path()

        # If file exists, load and return it
        if storage_path.exists():
            return load_tasks()

        # Create and save empty task list
        task_list = TaskList.create_empty()
        save_tasks(task_list)

        return task_list

    except StorageError:
        raise
    except Exception as e:
        raise StorageError(f"Error initializing storage: {e}")
