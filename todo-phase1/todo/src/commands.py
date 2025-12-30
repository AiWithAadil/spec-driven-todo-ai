"""Command implementations for todo CLI."""

from typing import Optional
from src.models import TaskList
from src.storage import load_tasks, save_tasks
from src.formatter import (
    format_confirmation, format_error, format_task_list, format_help, format_command_help
)
from src.errors import TaskNotFoundError, InvalidTaskError, CommandError


def add_task(description: str) -> str:
    """Add a new task.

    Args:
        description: Description of the task to add

    Returns:
        Confirmation message

    Raises:
        InvalidTaskError: If description is invalid
        StorageError: If save fails
    """
    try:
        # Load existing tasks
        task_list = load_tasks()

        # Add the task (validates description)
        task = task_list.add_task(description)

        # Save updated list
        save_tasks(task_list)

        # Return confirmation
        return format_confirmation(f"Task added (ID: {task.id})")

    except InvalidTaskError as e:
        return format_error(str(e))
    except Exception as e:
        return format_error(f"Failed to add task: {e}")


def list_tasks() -> str:
    """List all tasks.

    Returns:
        Formatted list of tasks

    Raises:
        StorageError: If load fails
    """
    try:
        task_list = load_tasks()
        tasks = task_list.get_all_tasks()
        return format_task_list(tasks)

    except Exception as e:
        return format_error(f"Failed to list tasks: {e}")


def complete_task(task_id_str: str) -> str:
    """Mark a task as complete.

    Args:
        task_id_str: String representation of task ID

    Returns:
        Confirmation message or error message

    Raises:
        TaskNotFoundError: If task not found
        CommandError: If ID is invalid
    """
    try:
        # Validate and parse task ID
        try:
            task_id = int(task_id_str)
            if task_id <= 0:
                return format_error("Invalid task ID (must be positive)")
        except ValueError:
            return format_error("Invalid task ID (must be a number)")

        # Load tasks
        task_list = load_tasks()

        # Find and mark complete
        task = task_list.find_task(task_id)
        task.mark_complete()

        # Save updated list
        save_tasks(task_list)

        return format_confirmation(f"Task {task_id} marked as complete")

    except TaskNotFoundError as e:
        return format_error(str(e))
    except Exception as e:
        return format_error(f"Failed to complete task: {e}")


def update_task(task_id_str: str, new_description: str) -> str:
    """Update a task's description.

    Args:
        task_id_str: String representation of task ID
        new_description: New description for the task

    Returns:
        Confirmation message or error message

    Raises:
        TaskNotFoundError: If task not found
        InvalidTaskError: If description is invalid
        CommandError: If ID is invalid
    """
    try:
        # Validate and parse task ID
        try:
            task_id = int(task_id_str)
            if task_id <= 0:
                return format_error("Invalid task ID (must be positive)")
        except ValueError:
            return format_error("Invalid task ID (must be a number)")

        # Load tasks
        task_list = load_tasks()

        # Find task and update description
        task = task_list.find_task(task_id)
        task.update_description(new_description)

        # Save updated list
        save_tasks(task_list)

        return format_confirmation(f"Task {task_id} updated")

    except TaskNotFoundError as e:
        return format_error(str(e))
    except InvalidTaskError as e:
        return format_error(str(e))
    except Exception as e:
        return format_error(f"Failed to update task: {e}")


def delete_task(task_id_str: str) -> str:
    """Delete a task.

    Args:
        task_id_str: String representation of task ID

    Returns:
        Confirmation message or error message

    Raises:
        TaskNotFoundError: If task not found
        CommandError: If ID is invalid
    """
    try:
        # Validate and parse task ID
        try:
            task_id = int(task_id_str)
            if task_id <= 0:
                return format_error("Invalid task ID (must be positive)")
        except ValueError:
            return format_error("Invalid task ID (must be a number)")

        # Load tasks
        task_list = load_tasks()

        # Find and remove task
        task_list.remove_task(task_id)

        # Save updated list
        save_tasks(task_list)

        return format_confirmation(f"Task {task_id} deleted")

    except TaskNotFoundError as e:
        return format_error(str(e))
    except Exception as e:
        return format_error(f"Failed to delete task: {e}")


def help_command(command: Optional[str] = None) -> str:
    """Show help information.

    Args:
        command: (optional) Specific command to show help for

    Returns:
        Help text
    """
    if command:
        return format_command_help(command)
    else:
        return format_help()
