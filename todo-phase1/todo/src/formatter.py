"""Output formatting for tasks and messages."""

from typing import List
from src.models import Task, TaskList


def format_task_row(task: Task) -> str:
    """Format a single task row for display.

    Args:
        task: Task to format

    Returns:
        Formatted task row string
    """
    # Status indicator (use ASCII-compatible symbols for cross-platform compatibility)
    status = "[X]" if task.completed else "[ ]"

    # Format: "ID. Description [Status]"
    return f"{task.id}. {task.description:<40} {status}"


def format_task_list(tasks: List[Task]) -> str:
    """Format a list of tasks for display.

    Args:
        tasks: List of tasks to format

    Returns:
        Formatted task list string
    """
    if not tasks:
        return "No tasks found"

    # Count completed tasks
    completed_count = sum(1 for task in tasks if task.completed)

    # Format each task
    lines = []
    for task in tasks:
        lines.append(format_task_row(task))

    # Add summary line
    total = len(tasks)
    summary = f"\n({total} tasks, {completed_count} complete)"

    return "\n".join(lines) + summary


def format_confirmation(message: str) -> str:
    """Format a confirmation message for success operations.

    Args:
        message: Confirmation message

    Returns:
        Formatted confirmation string with checkmark
    """
    return f"[OK] {message}"


def format_error(message: str) -> str:
    """Format an error message for failed operations.

    Args:
        message: Error message

    Returns:
        Formatted error string with "Error:" prefix
    """
    return f"Error: {message}"


def format_help() -> str:
    """Format the help message.

    Returns:
        Help text with all commands
    """
    help_text = """Usage: todo <command> [arguments]

Commands:
  add <description>        Add a new task
  list                     Show all tasks
  view                     Show all tasks (alias for list)
  complete <task-id>       Mark task as complete
  update <task-id> <desc>  Update task description
  delete <task-id>         Delete a task
  help [command]           Show this help

Examples:
  todo add "Buy groceries"
  todo list
  todo complete 1
  todo update 1 "Buy organic groceries"
  todo delete 1
"""
    return help_text


def format_command_help(command: str) -> str:
    """Format help for a specific command.

    Args:
        command: Command name

    Returns:
        Help text for the command, or error message if unknown
    """
    help_by_command = {
        "add": """Add a new task

Usage: todo add "<description>"

Arguments:
  description    Task description (1-1000 characters, non-empty)

Examples:
  todo add "Buy groceries"
  todo add "Call mom at 3pm"

Errors:
  - Empty description: Task description cannot be empty
  - Too long: Task description cannot exceed 1000 characters
""",

        "list": """Show all tasks

Usage: todo list

Displays:
  - All tasks with ID, description, and completion status
  - Task count and completion count
  - "No tasks found" if list is empty

Status indicators:
  [ ] = Incomplete task
  [X] = Completed task

Examples:
  todo list
  todo view  (alias)
""",

        "view": """Show all tasks (alias for list)

Usage: todo view

See: todo help list
""",

        "complete": """Mark a task as complete

Usage: todo complete <task-id>

Arguments:
  task-id    ID of the task to mark complete (must be a number)

Examples:
  todo complete 1
  todo complete 5

Errors:
  - Non-existent task: Task X not found
  - Invalid format: Invalid task ID (must be a number)
  - Negative/zero: Invalid task ID (must be positive)

Note: Marking an already-complete task is safe (idempotent).
""",

        "update": """Update a task description

Usage: todo update <task-id> "<new-description>"

Arguments:
  task-id           ID of the task to update
  new-description   New description (1-1000 characters, non-empty)

Examples:
  todo update 1 "Buy organic groceries"
  todo update 2 "Call mom after work"

Errors:
  - Non-existent task: Task X not found
  - Invalid format: Invalid task ID (must be a number)
  - Empty description: Task description cannot be empty
  - Too long: Task description cannot exceed 1000 characters
""",

        "delete": """Delete a task permanently

Usage: todo delete <task-id>

Arguments:
  task-id    ID of the task to delete

Examples:
  todo delete 1
  todo delete 3

Note: Deleted tasks cannot be recovered. Task IDs are never reused.

Errors:
  - Non-existent task: Task X not found
  - Invalid format: Invalid task ID (must be a number)
""",

        "help": """Show help information

Usage: todo help [command]

Arguments:
  command    (optional) Show help for specific command

Examples:
  todo help
  todo help add
  todo help complete
""",
    }

    if command in help_by_command:
        return help_by_command[command]
    else:
        return f"Unknown command: {command}\n\nRun 'todo help' for usage information."
