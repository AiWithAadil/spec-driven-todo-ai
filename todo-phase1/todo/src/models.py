"""Data models for Task and TaskList entities."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from src.errors import InvalidTaskError, TaskNotFoundError


class Task:
    """Represents a single todo item."""

    def __init__(
        self,
        task_id: int,
        description: str,
        completed: bool = False,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        """Initialize a Task.

        Args:
            task_id: Unique identifier for the task
            description: Task description (1-1000 characters)
            completed: Whether the task is completed
            created_at: ISO 8601 timestamp of creation
            updated_at: ISO 8601 timestamp of last update

        Raises:
            InvalidTaskError: If description is invalid
        """
        self.id = task_id
        self.completed = completed
        self.created_at = created_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.updated_at = updated_at

        # Validate and set description
        self.description = self._validate_description(description)

    @staticmethod
    def _validate_description(description: str) -> str:
        """Validate task description.

        Args:
            description: Description to validate

        Returns:
            Validated description

        Raises:
            InvalidTaskError: If description is invalid
        """
        if not isinstance(description, str):
            raise InvalidTaskError("Task description must be a string")

        stripped = description.strip()
        if not stripped:
            raise InvalidTaskError("Task description cannot be empty")

        if len(description) > 1000:
            raise InvalidTaskError("Task description cannot exceed 1000 characters")

        return description

    def update_description(self, new_description: str) -> None:
        """Update the task description.

        Args:
            new_description: New description for the task

        Raises:
            InvalidTaskError: If new description is invalid
        """
        self.description = self._validate_description(new_description)
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_complete(self) -> None:
        """Mark the task as complete."""
        self.completed = True
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the task
        """
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create a Task from a dictionary.

        Args:
            data: Dictionary with task data

        Returns:
            Task instance
        """
        return cls(
            task_id=data["id"],
            description=data["description"],
            completed=data.get("completed", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


class TaskList:
    """Collection of tasks with management operations."""

    def __init__(self, version: int = 1, next_id: int = 1, tasks: Optional[List[Task]] = None):
        """Initialize a TaskList.

        Args:
            version: Schema version for forward compatibility
            next_id: Next available task ID
            tasks: List of Task objects
        """
        self.version = version
        self.next_id = next_id
        self.tasks = tasks or []

    def add_task(self, description: str) -> Task:
        """Add a new task to the list.

        Args:
            description: Description of the new task

        Returns:
            The newly created Task

        Raises:
            InvalidTaskError: If description is invalid
        """
        # Validate description (raises InvalidTaskError if invalid)
        Task._validate_description(description)

        # Create new task with current next_id
        task = Task(
            task_id=self.next_id,
            description=description,
            completed=False
        )

        # Increment next_id for future tasks (never reuse IDs)
        self.next_id += 1

        # Add to task list
        self.tasks.append(task)

        return task

    def find_task(self, task_id: int) -> Task:
        """Find a task by ID.

        Args:
            task_id: ID of the task to find

        Returns:
            The Task with the specified ID

        Raises:
            TaskNotFoundError: If task is not found
        """
        for task in self.tasks:
            if task.id == task_id:
                return task

        raise TaskNotFoundError(f"Task {task_id} not found")

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks.

        Returns:
            List of all tasks in insertion order
        """
        return self.tasks

    def remove_task(self, task_id: int) -> None:
        """Remove a task by ID.

        Args:
            task_id: ID of the task to remove

        Raises:
            TaskNotFoundError: If task is not found
        """
        task = self.find_task(task_id)  # Raises TaskNotFoundError if not found
        self.tasks.remove(task)

    def to_dict(self) -> Dict[str, Any]:
        """Convert TaskList to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the task list
        """
        return {
            "version": self.version,
            "next_id": self.next_id,
            "tasks": [task.to_dict() for task in self.tasks]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskList":
        """Create a TaskList from a dictionary.

        Args:
            data: Dictionary with task list data

        Returns:
            TaskList instance
        """
        tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
        return cls(
            version=data.get("version", 1),
            next_id=data.get("next_id", len(tasks) + 1),
            tasks=tasks
        )

    @classmethod
    def create_empty(cls) -> "TaskList":
        """Create an empty TaskList.

        Returns:
            Empty TaskList with version 1 and next_id 1
        """
        return cls(version=1, next_id=1, tasks=[])
