"""Main CLI entry point for Todo application."""

import argparse
import sys
from src.commands import (
    add_task, list_tasks, complete_task, update_task, delete_task, help_command
)


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        prog="todo",
        description="A simple CLI todo application",
        add_help=False  # We'll handle help ourselves
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: add
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("description", help="Task description (1-1000 characters)")

    # Command: list
    subparsers.add_parser("list", help="Show all tasks")

    # Command: view (alias for list)
    subparsers.add_parser("view", help="Show all tasks (alias for list)")

    # Command: complete
    complete_parser = subparsers.add_parser("complete", help="Mark task as complete")
    complete_parser.add_argument("task_id", help="Task ID to mark complete")

    # Command: update
    update_parser = subparsers.add_parser("update", help="Update task description")
    update_parser.add_argument("task_id", help="Task ID to update")
    update_parser.add_argument("description", help="New task description")

    # Command: delete
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", help="Task ID to delete")

    # Command: help
    help_parser = subparsers.add_parser("help", help="Show help information")
    help_parser.add_argument("command", nargs="?", help="Specific command to get help for")

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "add":
        output = add_task(args.description)
        print(output)

    elif args.command in ("list", "view"):
        output = list_tasks()
        print(output)

    elif args.command == "complete":
        output = complete_task(args.task_id)
        print(output)

    elif args.command == "update":
        output = update_task(args.task_id, args.description)
        print(output)

    elif args.command == "delete":
        output = delete_task(args.task_id)
        print(output)

    elif args.command == "help":
        # Get the specific command to help for, if provided
        specific_command = getattr(args, "command", None)
        output = help_command(specific_command)
        print(output)

    else:
        # No command provided, show help
        output = help_command()
        print(output)


if __name__ == "__main__":
    main()
