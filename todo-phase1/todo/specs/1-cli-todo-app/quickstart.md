# Quickstart Guide: Python CLI Todo Application

**Feature**: 1-cli-todo-app | **Date**: 2025-12-29

This guide walks through the basic usage of the todo CLI application based on the implemented architecture.

## Installation

The application is a single Python module with no external dependencies.

```bash
# Copy the module to your system (or add to PATH)
cp src/todo_app.py /usr/local/bin/todo
chmod +x /usr/local/bin/todo

# Or run directly
python3 src/todo_app.py <command> <args>
```

## Getting Started

### Add Your First Task

```bash
$ todo add "Buy groceries"
✓ Task added (ID: 1)
```

### View Your Tasks

```bash
$ todo list
1. Buy groceries                       [ ]

(1 tasks, 0 complete)
```

### Add More Tasks

```bash
$ todo add "Call mom"
✓ Task added (ID: 2)

$ todo add "Review PR"
✓ Task added (ID: 3)

$ todo list
1. Buy groceries                       [ ]
2. Call mom                            [ ]
3. Review PR                           [ ]

(3 tasks, 0 complete)
```

### Mark Tasks Complete

Track your progress by marking tasks as done:

```bash
$ todo complete 1
✓ Task 1 marked as complete

$ todo complete 2
✓ Task 2 marked as complete

$ todo list
1. Buy groceries                       [✓]
2. Call mom                            [✓]
3. Review PR                           [ ]

(3 tasks, 2 complete)
```

### Update Tasks

Fix typos or refine task descriptions:

```bash
$ todo update 3 "Review PR from John"
✓ Task 3 updated

$ todo list
1. Buy groceries                       [✓]
2. Call mom                            [✓]
3. Review PR from John                 [ ]

(3 tasks, 2 complete)
```

### Delete Tasks

Remove tasks you no longer need:

```bash
$ todo delete 2
✓ Task 2 deleted

$ todo list
1. Buy groceries                       [✓]
3. Review PR from John                 [ ]

(2 tasks, 1 complete)
```

Note: Task IDs are never reused, so ID 2 won't appear again even after deletion.

---

## Common Workflows

### Daily Standup

Check your current tasks:

```bash
$ todo list
```

### Adding Tasks Throughout the Day

```bash
$ todo add "Respond to emails"
$ todo add "Lunch at noon"
$ todo add "Team meeting at 2pm"
```

### Completing Tasks as You Work

```bash
$ todo complete 4
$ todo complete 5
```

### End of Day Review

```bash
$ todo list  # See what's done and what's remaining
```

---

## Data Storage

Your tasks are automatically saved to:

**Linux/macOS**: `~/.todo/tasks.json`
**Windows**: `%USERPROFILE%\.todo\tasks.json`

The file is a simple JSON format that you can inspect:

```json
{
  "version": 1,
  "next_id": 4,
  "tasks": [
    {
      "id": 1,
      "description": "Buy groceries",
      "completed": true,
      "created_at": "2025-12-29T10:30:00Z",
      "updated_at": "2025-12-29T14:45:00Z"
    },
    {
      "id": 3,
      "description": "Review PR from John",
      "completed": false,
      "created_at": "2025-12-29T12:00:00Z",
      "updated_at": null
    }
  ]
}
```

**Note**: You can edit this file directly, but the app will overwrite it with each command. Use the CLI for safety.

---

## Error Handling

The app handles errors gracefully:

### Empty Description

```bash
$ todo add ""
Error: Task description cannot be empty
```

### Invalid Task ID

```bash
$ todo complete 99
Error: Task 99 not found
```

### Non-numeric ID

```bash
$ todo complete abc
Error: Invalid task ID (must be a number)
```

### No Panic

The app will never crash or corrupt your data, even with invalid input. Always try again with correct arguments.

---

## Help and Examples

Get help at any time:

```bash
$ todo help
Usage: todo <command> [arguments]

Commands:
  add <description>        Add a new task
  list or view             Show all tasks
  complete <task-id>       Mark task as complete
  update <task-id> <desc>  Update task description
  delete <task-id>         Delete a task
  help [command]           Show this help

Examples:
  todo add "Buy milk"
  todo list
  todo complete 1
```

Get help for a specific command:

```bash
$ todo help add
Add a new task

Usage: todo add "<description>"

Arguments:
  description    Task description (1-1000 characters)

Examples:
  todo add "Buy groceries"
  todo add "Call mom at 3pm"
```

---

## Tips and Tricks

### Viewing Tasks Without Running Commands

You can manually inspect your tasks file:

```bash
# Linux/macOS
cat ~/.todo/tasks.json | python3 -m json.tool

# Windows PowerShell
Get-Content $env:USERPROFILE\.todo\tasks.json | ConvertFrom-Json | ConvertTo-Json
```

### Backing Up Your Tasks

```bash
# Linux/macOS
cp ~/.todo/tasks.json ~/.todo/tasks.backup.json

# Windows PowerShell
Copy-Item $env:USERPROFILE\.todo\tasks.json $env:USERPROFILE\.todo\tasks.backup.json
```

### Starting Fresh

To delete all tasks and start over:

```bash
# Linux/macOS
rm ~/.todo/tasks.json

# Windows PowerShell
Remove-Item $env:USERPROFILE\.todo\tasks.json
```

The app will create a new task file on your next command.

---

## Architecture Overview (for developers)

### Module Structure

```
src/
├── todo_app.py       # Entry point, CLI argument parsing
├── models.py         # Task and TaskList data structures
├── storage.py        # File I/O (load/save)
├── commands.py       # Command implementations
├── formatter.py      # Output formatting
└── errors.py         # Custom exceptions
```

### Command Flow

```
User Input
    ↓
todo_app.py (parse args)
    ↓
commands.py (execute command)
    ↓
models.py (update in-memory state)
    ↓
storage.py (persist to disk)
    ↓
formatter.py (format output)
    ↓
stdout (display to user)
```

### Data Persistence

- Tasks are loaded into memory at startup
- All mutations trigger a save to disk
- JSON format ensures human readability and easy debugging

---

## Next Steps

- Start using the app to manage your tasks
- Run tests: `pytest tests/`
- Read the full architecture in `specs/1-cli-todo-app/plan.md`
- Check data model details in `specs/1-cli-todo-app/data-model.md`
- Review CLI contracts in `specs/1-cli-todo-app/contracts/cli-commands.md`
