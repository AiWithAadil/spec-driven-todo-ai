# Phase 1: Data Model & Database Schema

**Date**: 2025-12-31
**Feature**: Web-based Todo Application
**Status**: Complete

## Entity Relationship Diagram

```
User (1) ──── (M) Task
├─ id
├─ email
└─ hashed_password

Task
├─ id
├─ user_id (FK)
├─ title
├─ description
├─ is_completed
├─ created_at
└─ updated_at
```

---

## Detailed Entity Definitions

### User Entity

**Purpose**: Represents a registered user account. Owns multiple tasks. Authenticated via email and password.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique user identifier |
| email | String(255) | Unique, NOT NULL | User's email address (login identifier) |
| hashed_password | String(255) | NOT NULL | Bcrypt-hashed password (never stored plain) |
| created_at | DateTime | NOT NULL, Default: now | Account creation timestamp |

**Validations**:
- Email: Valid email format (RFC 5322), max 255 characters
- Password: Minimum 8 characters (enforced at API layer during registration)
- Unique constraint on email (prevents duplicate registrations)

**State Transitions**:
- Created: User registers with email + password
- Active: After successful registration, can immediately log in
- Deleted: (Out of scope for MVP) User account deletion

**SQL Definition**:
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

---

### Task Entity

**Purpose**: Represents a single todo item. Belongs to a user. Can be created, read, updated, and deleted.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique task identifier |
| user_id | Integer | FK → users(id), NOT NULL | Owner of the task |
| title | String(255) | NOT NULL | Task title/name |
| description | Text | Nullable, Default: '' | Optional task details |
| is_completed | Boolean | NOT NULL, Default: False | Completion status |
| created_at | DateTime | NOT NULL, Default: now | When task was created |
| updated_at | DateTime | NOT NULL, Default: now | When task was last modified |

**Validations**:
- title: Non-empty string, max 255 characters
- description: Optional, any text, max 10,000 characters
- is_completed: Boolean (true/false)
- user_id: Must reference existing user
- updated_at: Auto-updated on any modification

**State Transitions**:
```
Created (is_completed=False)
  ├─ → Updated (title/description change)
  ├─ → Completed (is_completed=True)
  │    └─ → Incomplete (is_completed=False)
  └─ → Deleted (removed from database)
```

**SQL Definition**:
```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT DEFAULT '',
  is_completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

**Cascade Behavior**: When user is deleted, all their tasks are deleted (ON DELETE CASCADE).

---

## Relationship Definitions

### User ↔ Task (One-to-Many)

**Relationship**: One user owns many tasks. Each task belongs to exactly one user.

**Cardinality**: (1:M)

**Foreign Key**: Task.user_id → User.id

**Constraints**:
- Each task must have a valid user_id
- User can have zero or more tasks
- Deleting a user deletes all their tasks
- Task cannot be reassigned to another user

**Query Examples**:
```sql
-- Get all tasks for a user
SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC;

-- Get user's completed tasks
SELECT * FROM tasks WHERE user_id = ? AND is_completed = TRUE;

-- Count user's tasks
SELECT COUNT(*) FROM tasks WHERE user_id = ?;
```

---

## Database Indexes

**Primary Indexes** (auto-created with primary keys):
- `users.id`
- `tasks.id`

**Foreign Key Indexes**:
- `tasks.user_id` → Fast user lookups, enforces referential integrity

**Performance Indexes**:
- `tasks.created_at` → Efficient sorting and filtering by creation date
- `users.email` → Fast login lookups

**Rationale**:
- Small dataset initially (100+ concurrent users, ~1000s tasks)
- Indexes optimize common queries: list user's tasks, filter by status
- Email index critical for login performance
- created_at index supports sorting tasks newest-first

---

## Data Integrity

### Uniqueness Constraints

```sql
-- User emails must be unique
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE(email);
```

### Referential Integrity

```sql
-- Tasks must reference valid users; cascade on deletion
ALTER TABLE tasks
  ADD CONSTRAINT fk_tasks_user_id
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

### Required Fields

- users.email: NOT NULL
- users.hashed_password: NOT NULL
- tasks.user_id: NOT NULL
- tasks.title: NOT NULL

### Default Values

- tasks.is_completed: FALSE
- tasks.description: '' (empty string)
- tasks.created_at: CURRENT_TIMESTAMP
- tasks.updated_at: CURRENT_TIMESTAMP

---

## Pydantic Schemas (Python Request/Response Models)

Used by FastAPI for validation and OpenAPI documentation.

### UserSchema (Base)
```python
class UserSchema(BaseModel):
    id: int
    email: str
    created_at: datetime

class Config:
    from_attributes = True
```

### UserRegisterSchema
```python
class UserRegisterSchema(BaseModel):
    email: EmailStr  # Validates email format
    password: str    # Min 8 chars enforced in service layer
    password_confirm: str
```

### UserLoginSchema
```python
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
```

### UserResponseSchema
```python
class UserResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSchema
```

### TaskSchema (Base)
```python
class TaskSchema(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### TaskCreateSchema
```python
class TaskCreateSchema(BaseModel):
    title: str  # Max 255 chars, non-empty (enforced by API)
    description: str = ""  # Optional
```

### TaskUpdateSchema
```python
class TaskUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None
```

### TaskListSchema
```python
class TaskListSchema(BaseModel):
    tasks: list[TaskSchema]
    total: int
```

---

## Migration Strategy

**Tool**: Alembic (SQLAlchemy migration framework)

**Initial Setup**:
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial schema: users and tasks"
alembic upgrade head
```

**Workflow**:
1. Update SQLAlchemy models in `models.py`
2. Auto-generate migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration (in `alembic/versions/`)
4. Apply migration: `alembic upgrade head`
5. Commit migration files to git

**Rollback**:
```bash
alembic downgrade -1  # Roll back last migration
```

---

## Assumptions & Out of Scope

### Assumptions
- Email is the unique, immutable user identifier
- Tasks cannot be shared or reassigned to other users
- Soft deletes not needed (hard delete on task removal)
- No audit log or history of task changes
- No bulk operations (delete all, archive completed, etc.)

### Out of Scope (Not in MVP)
- Task categories or tags
- Task due dates or priorities
- Task sub-tasks or dependencies
- Recurring tasks
- Task sharing or collaboration
- Undo/restore deleted tasks
- User profile fields (name, avatar, preferences)
- Data export/import
- User account deletion API
- Password reset/recovery

---

## Performance Considerations

**Query Patterns**:
- List tasks for user: O(n) where n = user's tasks (typical <1000)
- Create task: O(1)
- Update task: O(1)
- Delete task: O(1)

**Scalability**:
- Handles 100+ concurrent users easily
- Simple schema, minimal query complexity
- Indexes on common filters (user_id, created_at, email)
- Pagination added to list endpoint if needed (not in MVP)

**Storage**:
- User: ~256 bytes per row
- Task: ~512 bytes per row
- 10,000 users × 1,000 tasks = ~5GB data (acceptable for MVP)

---

## Summary

| Aspect | Decision |
|--------|----------|
| Schema | Two tables: users + tasks with 1:M relationship |
| Integrity | Foreign key constraints, unique email, cascading deletes |
| Indexes | On user_id, email (login), created_at (sorting) |
| ORM | SQLAlchemy 2.0+ with auto-validation via Pydantic |
| Migrations | Alembic for version control and rollback |
| Scalability | Supports MVP scale; indexed for common queries |
