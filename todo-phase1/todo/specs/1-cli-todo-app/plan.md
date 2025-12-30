# Implementation Plan: Python CLI Todo Application

**Branch**: `1-cli-todo-app` | **Date**: 2025-12-29 | **Spec**: [specs/1-cli-todo-app/spec.md](./spec.md)

**Input**: Feature specification for a Python CLI Todo application with five core features: add, view, complete, update, and delete tasks.

## Summary

Implement a lightweight, single-file Python CLI application that manages a todo list with in-memory data structures and simple file-based persistence. The application will support five operations (add, view, complete, update, delete) through a command-line interface with clear error handling and confirmation messages.

## Technical Context

**Language/Version**: Python 3.8+
**Primary Dependencies**: None (standard library only - `argparse`, `json`, `pathlib`)
**Storage**: JSON file (`~/.todo/tasks.json` or `./tasks.json`)
**Testing**: `pytest` with test fixtures
**Target Platform**: Linux, macOS, Windows (any platform with Python 3.8+)
**Project Type**: Single CLI application
**Performance Goals**: Sub-100ms response time for all operations
**Constraints**: Single-user, no concurrency control, in-memory task list during session
**Scale/Scope**: Support 1000+ tasks with minimal memory footprint

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Status**: Not yet defined for this project (using defaults).

**Applicable Principles**:
- ✅ **Simplicity**: Single-file implementation preferred; no frameworks or unnecessary abstractions
- ✅ **Clarity**: Command-line interface with explicit, user-friendly output
- ✅ **Testability**: All operations must be unit-testable and integration-testable
- ✅ **Data Persistence**: Tasks must survive application restarts (JSON storage)
- ✅ **Error Handling**: Clear, actionable error messages for all failure scenarios

**Gate Evaluation**: PASS - Simple architecture aligns with specification constraints and principle of minimalism.

## Project Structure

### Documentation (this feature)

```text
specs/1-cli-todo-app/
├── spec.md              # Feature specification
├── plan.md              # This file (implementation plan)
├── research.md          # Design research and decisions
├── data-model.md        # Data structures and entities
├── quickstart.md        # Getting started guide
├── contracts/           # API contracts
│   └── cli-commands.md  # Command-line interface contract
└── checklists/
    └── requirements.md  # Quality validation
```

### Source Code (repository root)

```text
src/
├── todo_app.py          # Main application entry point (CLI + command dispatcher)
├── models.py            # Task model and data structures
├── storage.py           # File persistence layer
├── commands.py          # Command implementations (add, view, delete, update, complete)
├── formatter.py         # Output formatting and display logic
└── errors.py            # Custom exception types

tests/
├── test_models.py       # Unit tests for Task entity
├── test_storage.py      # Unit tests for persistence layer
├── test_commands.py     # Unit tests for command logic
├── test_integration.py  # End-to-end CLI tests
└── fixtures/
    └── sample_data.py   # Test data fixtures

README.md                # User documentation
requirements.txt         # Python dependencies (empty for this version)
```

**Structure Decision**: Single-project layout with clear separation of concerns (models, storage, commands, formatting). This supports testability while keeping the application lightweight. All dependencies are standard library, requiring no external packages.

## Key Design Decisions

### 1. Data Storage

**Decision**: JSON file-based storage in user's home directory (`~/.todo/tasks.json`)

**Rationale**:
- Meets specification requirement for data persistence across restarts
- Simple, human-readable format
- No external dependencies (uses `json` module)
- Easy to inspect and debug
- Sufficient for single-user, local-only use case

**Alternatives Considered**:
- SQLite: Overcomplicated for this use case; adds dependency and complexity
- In-memory only: Violates FR-007 (persistence requirement)
- CSV: Less structured; harder to handle special characters in task descriptions

### 2. Task Identification

**Decision**: Auto-incrementing numeric IDs (1, 2, 3, ...) stored in JSON metadata

**Rationale**:
- Specification assumes simple index/ID system (see Assumptions section of spec)
- IDs never reused (persist across deletes) to avoid user confusion
- Simpler than UUIDs for single-user CLI
- Easy for users to reference in commands

**Alternatives Considered**:
- UUIDs: Overkill; difficult for users to type and remember
- Array indices: Would change when tasks deleted (poor UX)

### 3. Command Structure

**Decision**: Single entry point (`todo`) with subcommands using `argparse`

**Rationale**:
- Standard Unix CLI pattern (`git`, `docker`, `aws`)
- Clean separation of command logic in `commands.py`
- Easy to extend with new commands
- Built-in help and error handling

**Example Commands**:
```bash
todo add "Buy groceries"
todo list
todo view
todo complete 1
todo update 1 "Buy organic groceries"
todo delete 1
```

### 4. Error Handling

**Decision**: Custom exception hierarchy with user-friendly error messages

**Rationale**:
- FR-006 requires clear error messages for invalid task IDs
- Consistent error reporting across all commands
- Testable error scenarios

**Exception Types**:
- `TaskNotFoundError`: Invalid task ID
- `InvalidTaskError`: Empty or invalid task description
- `StorageError`: File I/O failures
- `CommandError`: Invalid command arguments

### 5. Session vs. Persistence

**Decision**: Load all tasks into memory at startup; persist after each mutation

**Rationale**:
- Simple implementation; no complex locking needed
- Fast query performance (in-memory lookup)
- Safe by design (data always persisted after mutation)
- Suitable for single-user use case

**Alternatives Considered**:
- Lazy loading: More complex; not needed for small task lists
- In-memory only: Violates persistence requirement
- Atomic file writes: Unnecessary complexity for single-user

## Data Model

### Task Entity

```python
Task = {
    "id": int,                    # Auto-incrementing, never reused
    "description": str,           # Plain text, 1-1000 characters
    "completed": bool,            # true/false
    "created_at": str,           # ISO 8601 timestamp (optional, for future use)
    "updated_at": str            # ISO 8601 timestamp (optional, for future use)
}
```

### Task List Storage

```json
{
  "version": 1,
  "next_id": 3,
  "tasks": [
    {
      "id": 1,
      "description": "Buy groceries",
      "completed": false,
      "created_at": "2025-12-29T10:30:00Z"
    },
    {
      "id": 2,
      "description": "Call mom",
      "completed": true,
      "created_at": "2025-12-29T11:00:00Z"
    }
  ]
}
```

## Command Contracts

### `todo add "<description>"`

**Input**:
- `<description>`: Required string (1-1000 characters, non-empty)

**Output (Success)**:
```
✓ Task added (ID: 1)
```

**Output (Error)**:
```
Error: Task description cannot be empty
```

### `todo list` / `todo view`

**Input**: None

**Output (with tasks)**:
```
1. Buy groceries [  ]
2. Call mom     [✓]
```

**Output (empty)**:
```
No tasks found
```

### `todo complete <task-id>`

**Input**:
- `<task-id>`: Required integer (must exist)

**Output (Success)**:
```
✓ Task 1 marked as complete
```

**Output (Error)**:
```
Error: Task 1 not found
```

### `todo update <task-id> "<new-description>"`

**Input**:
- `<task-id>`: Required integer (must exist)
- `<new-description>`: Required string (1-1000 characters, non-empty)

**Output (Success)**:
```
✓ Task 1 updated
```

**Output (Error)**:
```
Error: Task 1 not found
```

### `todo delete <task-id>`

**Input**:
- `<task-id>`: Required integer (must exist)

**Output (Success)**:
```
✓ Task 1 deleted
```

**Output (Error)**:
```
Error: Task 1 not found
```

## Complexity Justification

This plan uses a minimal stack to satisfy the specification:

| Aspect | Approach | Justification |
|--------|----------|---------------|
| Language | Python 3.8+ | Meets requirement; no framework bloat |
| Storage | Single JSON file | Simple persistence; no DB overhead |
| CLI | `argparse` (stdlib) | Standard tool; zero external dependencies |
| Testing | `pytest` | Industry standard; lightweight |
| Modules | 5 files | Clear separation of concerns; each <250 LOC |

## Next Steps (Phase 2)

After architectural approval, Phase 2 will generate `tasks.md` with:

1. **Task breakdown**: 15-20 atomic, independently testable tasks
2. **Dependency ordering**: Critical path for implementation
3. **Acceptance criteria**: Each task includes Given-When-Then scenarios
4. **Test cases**: Specific test implementations for each task
5. **Integration points**: How tasks connect and what data flows between them

Example Phase 2 tasks:
- Create Task model with validation
- Implement storage layer (load/save)
- Build command dispatcher
- Implement add command with tests
- Implement view command with formatting
- Implement delete/update/complete commands
- End-to-end integration tests
- CLI entry point and help system

---

**Architecture Status**: Ready for Phase 1 design work (data-model.md, contracts, quickstart)

**Gate Result**: ✅ PASS - Simple, testable architecture aligned with specification and principles of minimalism
