# Data Model: Python CLI Todo Application

**Feature**: 1-cli-todo-app | **Date**: 2025-12-29

## Core Entities

### Task

Represents a single todo item managed by the application.

#### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | `int` | Primary key, auto-increment, never reused | Unique identifier for the task. IDs are never recycled even after deletion to avoid confusion. |
| `description` | `str` | Required, 1-1000 characters, non-empty | Plain text description of the task. Cannot be empty or whitespace-only. |
| `completed` | `bool` | Required, default: `false` | Completion status of the task. Changed by "mark complete" operation. |
| `created_at` | `str` | ISO 8601 timestamp | Timestamp when task was created (for future sorting/filtering). |
| `updated_at` | `str` | ISO 8601 timestamp, nullable | Timestamp when task was last modified. Null if never updated. |

#### Validation Rules

- **Description cannot be empty**: `len(description.strip()) > 0`
- **Description max length**: `len(description) <= 1000`
- **ID must be positive**: `id > 0`
- **Completed is boolean**: `isinstance(completed, bool)`

#### State Transitions

```
┌─────────────────────────────────────┐
│   Task Created                      │
│   (completed = false)               │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
   Complete       Update description
        │             │
        ▼             ▼
  ┌──────────┐  ┌──────────┐
  │Completed │  │Updated   │
  │(no revert)   │(by update)
  └──────────┘  └──────────┘
```

**Operations**:
- **Create**: Transition from non-existent to new task with `completed=false`
- **Update**: Modify description (any state); updates `updated_at`
- **Complete**: Toggle `completed` to `true`; no state transition back
- **Delete**: Remove task from collection (end state)

#### Example Representations

```python
# Python object representation
task = {
    "id": 1,
    "description": "Buy groceries",
    "completed": False,
    "created_at": "2025-12-29T10:30:00Z",
    "updated_at": None
}

# After marking complete
task = {
    "id": 1,
    "description": "Buy groceries",
    "completed": True,
    "created_at": "2025-12-29T10:30:00Z",
    "updated_at": "2025-12-29T14:45:00Z"
}
```

---

### TaskList (Collection)

Container managing all tasks for a single user.

#### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `version` | `int` | Read-only, immutable | Schema version for forward compatibility. Currently `1`. |
| `next_id` | `int` | Read-only, auto-increment | Next available task ID. Ensures IDs never reuse. |
| `tasks` | `list[Task]` | Ordered collection | All tasks, maintained in insertion order. |

#### Invariants

- `next_id` is always greater than the highest existing task ID
- `next_id` increments with each new task, never decrements
- All task IDs in `tasks` are unique
- All tasks satisfy their validation rules

#### Storage Format (JSON)

```json
{
  "version": 1,
  "next_id": 5,
  "tasks": [
    {
      "id": 1,
      "description": "Buy groceries",
      "completed": false,
      "created_at": "2025-12-29T10:30:00Z",
      "updated_at": null
    },
    {
      "id": 2,
      "description": "Call mom",
      "completed": true,
      "created_at": "2025-12-29T11:00:00Z",
      "updated_at": "2025-12-29T14:00:00Z"
    },
    {
      "id": 4,
      "description": "Review PR",
      "completed": false,
      "created_at": "2025-12-29T12:00:00Z",
      "updated_at": null
    }
  ]
}
```

**Note**: Task with ID 3 was deleted; `next_id` is now 5 (not 4) because it tracks the highest ever issued.

---

## Operations

### Add Task

**Input**: Task description (string)

**Process**:
1. Validate description (non-empty, length <= 1000)
2. Create new Task object with:
   - `id = next_id`
   - `description = input`
   - `completed = false`
   - `created_at = now (ISO 8601)`
   - `updated_at = null`
3. Increment `next_id`
4. Append to `tasks` list
5. Persist to storage

**Output**: New task ID

**Error Cases**:
- Empty description → `InvalidTaskError`
- Description > 1000 chars → `InvalidTaskError`
- Storage failure → `StorageError`

### View/List Tasks

**Input**: None

**Process**:
1. Load all tasks from storage
2. Format for display:
   - Show ID, description, completion status
   - Completed tasks marked with `[✓]` or similar
   - Incomplete tasks marked with `[ ]`
3. Display in ID order

**Output**: Formatted task list

**Display Format**:
```
ID  Description         Status
──  ──────────────────  ──────
1   Buy groceries       [ ]
2   Call mom            [✓]
4   Review PR           [ ]

(3 tasks, 1 complete)
```

**Edge Cases**:
- Empty task list → Display "No tasks found"

### Mark Complete

**Input**: Task ID (integer)

**Process**:
1. Look up task by ID
2. Set `completed = true`
3. Set `updated_at = now (ISO 8601)`
4. Persist to storage

**Output**: Confirmation message

**Error Cases**:
- Task not found → `TaskNotFoundError`
- Invalid ID format → `CommandError`
- Storage failure → `StorageError`

### Update Description

**Input**: Task ID (integer), new description (string)

**Process**:
1. Look up task by ID
2. Validate new description (non-empty, length <= 1000)
3. Set `description = new_description`
4. Set `updated_at = now (ISO 8601)`
5. Persist to storage

**Output**: Confirmation message

**Error Cases**:
- Task not found → `TaskNotFoundError`
- Invalid description → `InvalidTaskError`
- Invalid ID format → `CommandError`
- Storage failure → `StorageError`

### Delete Task

**Input**: Task ID (integer)

**Process**:
1. Look up task by ID
2. Remove from `tasks` list
3. Do NOT decrement `next_id`
4. Persist to storage

**Output**: Confirmation message

**Error Cases**:
- Task not found → `TaskNotFoundError`
- Invalid ID format → `CommandError`
- Storage failure → `StorageError`

---

## Relationships

### Task ↔ TaskList

- **Composition**: TaskList contains many Tasks
- **Lifecycle**: Task is deleted when removed from TaskList
- **Referential integrity**: All task IDs in TaskList are unique and valid

### Task ↔ Persistent Storage

- **Persistence**: Each mutation operation triggers a write to disk
- **Format**: JSON serialization (described above)
- **Durability**: Sync write ensures durability for single-user use case

---

## Constraints & Assumptions

### Data Constraints

- Single-user, local application (no multi-user access)
- No concurrent operations (sequential CLI invocations)
- Task list fits entirely in memory (sub-MB for 1000+ tasks)
- Description is plain text (no special encoding needed beyond JSON)

### Technical Constraints

- Python 3.8+ (uses standard `json` module)
- File system must support JSON files (virtually all modern systems)
- No external dependencies (standard library only)

### Design Assumptions

- IDs never reset or reuse (monotonic increment)
- Task deletion is permanent (no soft deletes or archival)
- Completed tasks remain in list (not hidden or moved)
- Timestamps are optional for MVP but included for future features
- No audit trail or history (only current state persisted)

---

## Future Extensibility

This model supports planned expansions:

- **Task categories/tags**: Add `tags: list[str]` to Task
- **Task priority**: Add `priority: int` (1-5) to Task
- **Task due dates**: Add `due_at: str` (ISO 8601) to Task
- **Recurring tasks**: Add `recurrence: str` to Task
- **Task notes**: Add `notes: str` to Task
- **Archival**: Track deleted tasks in separate collection

None of these require schema changes; just add optional fields and ignore in MVP.
