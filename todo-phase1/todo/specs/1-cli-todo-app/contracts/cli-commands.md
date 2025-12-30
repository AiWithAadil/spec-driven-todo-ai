# CLI Command Contracts: Python CLI Todo Application

**Feature**: 1-cli-todo-app | **Date**: 2025-12-29

This document defines the command-line interface contract for the todo application. All commands follow Unix conventions and are tested against these specifications.

---

## Global Conventions

### Command Format

```
todo <command> [arguments]
```

### Exit Codes

- `0`: Success
- `1`: General error (invalid arguments, operation failed)
- `2`: Command not found

### Output Streams

- **Success messages**: stdout
- **Error messages**: stderr
- **Results**: stdout (formatted output)

### Error Message Format

```
Error: <clear description of what went wrong>
```

Example:
```
Error: Task 5 not found
```

### Confirmation Message Format

```
✓ <confirmation of what was done>
```

Example:
```
✓ Task added (ID: 1)
```

---

## Command: `todo add`

Add a new task to the todo list.

### Syntax

```
todo add "<description>"
```

### Arguments

| Argument | Type | Required | Constraints |
|----------|------|----------|-------------|
| `description` | string | Yes | 1-1000 characters, non-empty (after whitespace trim) |

### Examples

```bash
$ todo add "Buy groceries"
✓ Task added (ID: 1)

$ todo add "Call mom at 3pm"
✓ Task added (ID: 2)

$ todo add ""
Error: Task description cannot be empty

$ todo add "x"  # Valid: single character
✓ Task added (ID: 3)
```

### Acceptance Tests

1. **Valid task**: `todo add "Buy milk"` → Confirmation with ID, task appears in list
2. **Empty string**: `todo add ""` → Error message, no task created
3. **Whitespace only**: `todo add "   "` → Error message, no task created
4. **Long description**: `todo add "a"*1000` → Success
5. **Long description exceeds limit**: `todo add "a"*1001` → Error message
6. **Special characters**: `todo add "Fix bug: user@domain.com (critical!)"` → Success
7. **Quotes in description**: `todo add 'Task: say "hello"'` → Success
8. **Rapid adds**: Add 100 tasks rapidly → All created with unique IDs

### Implementation Constraints

- Must validate description before storing
- Must assign unique, auto-incrementing ID
- Must set `created_at` timestamp
- Must persist immediately to storage
- Must not crash on any input

---

## Command: `todo list` / `todo view`

Display all tasks in the todo list.

### Syntax

```
todo list
# or
todo view
```

### Arguments

None

### Examples

```bash
$ todo list
1. Buy groceries                       [ ]
2. Call mom                            [✓]
3. Review PR                           [ ]

(3 tasks, 1 complete)

$ todo list  # Empty list
No tasks found

$ todo list  # After all tasks complete
1. Buy groceries                       [✓]
2. Call mom                            [✓]
3. Review PR                           [✓]

(3 tasks, 3 complete)
```

### Output Format

```
ID  Description                        Status
─── ────────────────────────────────── ──────
1   Buy groceries                      [ ]
2   Call mom                           [✓]
```

**Elements**:
- ID: Task ID (right-aligned, 3 characters)
- Description: Task description (truncated to fit terminal if needed)
- Status: `[ ]` for incomplete, `[✓]` for complete
- Summary line: "(N tasks, M complete)"

### Acceptance Tests

1. **Empty list**: Display "No tasks found"
2. **Single task**: Show formatted row with ID 1
3. **Multiple tasks**: All tasks shown in order, all info visible
4. **Mixed status**: Completed tasks show `[✓]`, incomplete show `[ ]`
5. **Long descriptions**: Descriptions show in full (or truncated with `...` if terminal too narrow)
6. **Special characters**: All characters render correctly (test Unicode, quotes, etc.)
7. **Task count**: Summary line accurate for all task counts

### Implementation Constraints

- Must load all tasks from storage
- Must display in task ID order (ascending)
- Must show all tasks (no pagination for MVP)
- Must show completion status clearly
- Must handle empty list gracefully

---

## Command: `todo complete`

Mark a task as complete.

### Syntax

```
todo complete <task-id>
```

### Arguments

| Argument | Type | Required | Constraints |
|----------|------|----------|-------------|
| `task-id` | integer | Yes | Must be positive integer, must exist |

### Examples

```bash
$ todo complete 1
✓ Task 1 marked as complete

$ todo complete 1
✓ Task 1 marked as complete  # Idempotent: marking already-complete task is ok

$ todo complete 99
Error: Task 99 not found

$ todo complete abc
Error: Invalid task ID (must be a number)

$ todo complete 0
Error: Invalid task ID (must be positive)
```

### Acceptance Tests

1. **Valid task**: Mark task complete, verify status in list
2. **Non-existent ID**: Show error message, no state change
3. **Invalid ID format**: Show error message
4. **Negative ID**: Show error message
5. **Already complete**: Idempotent; mark again with no error
6. **Persistence**: After marking complete, app restart preserves status

### Implementation Constraints

- Must validate task ID (numeric, exists)
- Must set `completed = true`
- Must set `updated_at` timestamp
- Must persist immediately
- Must be idempotent (marking complete twice is safe)

---

## Command: `todo update`

Update a task's description.

### Syntax

```
todo update <task-id> "<new-description>"
```

### Arguments

| Argument | Type | Required | Constraints |
|----------|------|----------|-------------|
| `task-id` | integer | Yes | Must be positive integer, must exist |
| `new-description` | string | Yes | 1-1000 characters, non-empty |

### Examples

```bash
$ todo update 1 "Buy organic groceries"
✓ Task 1 updated

$ todo update 99 "Some task"
Error: Task 99 not found

$ todo update 1 ""
Error: Task description cannot be empty

$ todo update 1 "   "
Error: Task description cannot be empty

$ todo update abc "New task"
Error: Invalid task ID (must be a number)
```

### Acceptance Tests

1. **Valid update**: Change description, verify in list
2. **Empty new description**: Show error, no change
3. **Non-existent ID**: Show error, no state change
4. **Invalid ID format**: Show error message
5. **Update completed task**: Works; updates description of completed task
6. **Update with special characters**: Works with quotes, unicode, etc.
7. **Persistence**: After update, restart preserves new description

### Implementation Constraints

- Must validate task ID (numeric, exists)
- Must validate new description (non-empty, max 1000 chars)
- Must update `description` field
- Must set `updated_at` timestamp
- Must persist immediately
- Must not change completion status or ID

---

## Command: `todo delete`

Delete a task permanently.

### Syntax

```
todo delete <task-id>
```

### Arguments

| Argument | Type | Required | Constraints |
|----------|------|----------|-------------|
| `task-id` | integer | Yes | Must be positive integer, must exist |

### Examples

```bash
$ todo delete 1
✓ Task 1 deleted

$ todo delete 1
Error: Task 1 not found  # Already deleted

$ todo delete 99
Error: Task 99 not found

$ todo delete abc
Error: Invalid task ID (must be a number)

$ todo list  # After deleting task 1
2. Call mom                            [✓]
3. Review PR                           [ ]

(2 tasks, 1 complete)
```

### Acceptance Tests

1. **Valid delete**: Task removed, no longer in list
2. **Delete non-existent**: Show error, no state change
3. **Invalid ID format**: Show error message
4. **Delete already-deleted**: Show "not found" error
5. **ID reuse**: Deleted task ID never reused; next task gets new ID
6. **Persistence**: After delete, restart confirms task is gone
7. **Delete completed task**: Works; completed tasks can be deleted

### Implementation Constraints

- Must validate task ID (numeric, exists)
- Must remove task from storage
- Must NOT reuse the deleted task's ID
- Must persist immediately
- Must update task count in summary

---

## Command: `todo help`

Show command help.

### Syntax

```
todo help [command]
```

### Examples

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

$ todo help add
Add a new task

Usage: todo add "<description>"

Arguments:
  description    Task description (1-1000 characters)

Examples:
  todo add "Buy groceries"
  todo add "Call mom at 3pm"
```

### Acceptance Tests

1. **No arguments**: Show general help with all commands
2. **With command**: Show help for specific command
3. **Invalid command**: Show "Unknown command" error

---

## Global Error Handling

### Invalid Commands

```bash
$ todo invalid
Error: Unknown command 'invalid'

Run 'todo help' for usage information.
```

### Missing Arguments

```bash
$ todo add
Error: Missing required argument: description

Run 'todo help add' for usage information.
```

### Too Many Arguments

```bash
$ todo add "Task 1" "Task 2"
Error: Too many arguments

Run 'todo help add' for usage information.
```

---

## Testing Strategy

All commands are tested via:

1. **Unit tests**: Individual command logic
2. **Integration tests**: CLI argument parsing + command execution
3. **End-to-end tests**: Full command sequences with persistent storage

Example test flow:
```
add "Task 1" → add "Task 2" → complete 1 → list → delete 1 → list → verify
```

---

## Non-Functional Requirements

### Response Time

- All commands must complete in <1 second
- List command must display instantly even with 1000 tasks

### Error Messages

- All error messages must be on stderr
- All error messages must be actionable (user understands what went wrong)
- No stack traces or technical jargon

### Data Integrity

- Every mutation (add, update, delete, complete) must be immediately persisted
- No data loss on normal exit
- App crash must not corrupt stored data

### Usability

- Command syntax must follow Unix conventions
- Help text must be clear and include examples
- Error messages must suggest corrective actions
