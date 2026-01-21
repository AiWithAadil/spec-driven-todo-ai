# Data Model: AI-Powered Todo Chatbot

**Feature**: AI-Powered Todo Chatbot
**Created**: 2026-01-02
**Status**: Phase 1 Design

## Entity Overview

The system persists four core entities: Conversations, Messages, Todos, and ToolInvocations. All state is stored in PostgreSQL via SQLModel ORM. No in-memory state is maintained between requests.

## Entities and Schemas

### 1. Conversation

Represents a single chat session between a user and the chatbot.

**Purpose**: Track conversation context and enable session resumption.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique conversation identifier |
| `user_id` | string | Required, indexed | User identifier (from auth) |
| `created_at` | datetime | Required, default now | Conversation creation timestamp |
| `last_updated_at` | datetime | Required, default now | Last message timestamp |

**Relationships**:
- Has many `Messages` (1:N)
- May have many `Todos` (created within this conversation)

**Validation Rules**:
- `user_id` must be non-empty string
- `created_at` ≤ `last_updated_at`
- `id` is immutable (UUID generated on creation)

**State Transitions**:
- New → Active (when first message added)
- Active → Archived (when no messages for 90 days; soft-archive)

**Indexes**:
- `(user_id, created_at)` — fast retrieval of user's conversations
- `id` — primary key lookup

**Example**:
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "user_id": "user123",
  "created_at": "2026-01-02T10:00:00Z",
  "last_updated_at": "2026-01-02T10:15:30Z"
}
```

---

### 2. Message

Represents a single exchange in a conversation (either user input or agent response).

**Purpose**: Store conversation history for context and resumption.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique message identifier |
| `conversation_id` | UUID | Required, FK → Conversation.id | Associated conversation |
| `role` | enum | Required, enum['user', 'assistant'] | Message sender |
| `content` | text | Required | Full message text |
| `timestamp` | datetime | Required, default now | Message creation time |

**Relationships**:
- Belongs to `Conversation` (N:1)
- Has many `ToolInvocations` (1:N) — if role = 'assistant'

**Validation Rules**:
- `role` must be 'user' or 'assistant'
- `content` must be non-empty, max 10,000 characters
- `timestamp` ≤ now()
- `conversation_id` must reference existing conversation

**Immutability**:
- `id`, `conversation_id`, `role`, `timestamp` are immutable
- `content` is immutable (no edits; delete and re-add if needed)

**Indexes**:
- `(conversation_id, timestamp)` — load conversation history in order

**Example**:
```json
{
  "id": "a1b2c3d4-5e6f-7a8b-9c0d-e1f2a3b4c5d6",
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "role": "user",
  "content": "Create a todo to buy groceries",
  "timestamp": "2026-01-02T10:01:00Z"
}
```

---

### 3. Todo

Represents a task managed by the user.

**Purpose**: Store todo state for retrieval and updates via MCP tools.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique todo identifier |
| `user_id` | string | Required, indexed | User who owns todo |
| `title` | string | Required, max 200 chars | Todo title/name |
| `description` | text | Optional, max 5,000 chars | Detailed description |
| `status` | enum | Required, enum['open', 'completed', 'archived'], default 'open' | Todo state |
| `priority` | enum | Required, enum['low', 'medium', 'high'], default 'medium' | Priority level |
| `created_at` | datetime | Required, default now | Creation timestamp |
| `updated_at` | datetime | Required, default now | Last update timestamp |
| `created_in_conversation_id` | UUID | Optional, FK → Conversation.id | Conversation where todo was created |

**Relationships**:
- Belongs to `Conversation` (N:1, optional) — originating conversation
- Owned by User (implicitly via `user_id`)

**Validation Rules**:
- `title` must be non-empty, max 200 characters
- `description` max 5,000 characters
- `status` must be one of: 'open', 'completed', 'archived'
- `priority` must be one of: 'low', 'medium', 'high'
- `created_at` ≤ `updated_at`
- `user_id` must be non-empty

**State Transitions**:
- New → open (on creation)
- open → completed (mark complete)
- open/completed → archived (archive)
- completed → open (un-complete)
- Any → deleted (soft-delete or hard-delete; per implementation choice)

**Indexes**:
- `(user_id, status, updated_at)` — fast list todos for user
- `(user_id, created_in_conversation_id)` — list todos created in specific conversation

**Example**:
```json
{
  "id": "c8d9e0f1-a2b3-4c5d-6e7f-8a9b0c1d2e3f",
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "open",
  "priority": "medium",
  "created_at": "2026-01-02T10:01:30Z",
  "updated_at": "2026-01-02T10:01:30Z",
  "created_in_conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

---

### 4. ToolInvocation

Represents a single MCP tool call during agent processing (audit log).

**Purpose**: Track all tool invocations for debugging, auditing, and observability.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique invocation identifier |
| `message_id` | UUID | Required, FK → Message.id | Associated message |
| `tool_name` | string | Required, enum['create_todo', 'read_todos', 'update_todo', 'delete_todo'] | Tool invoked |
| `parameters` | jsonb | Required | Input parameters to tool (JSON) |
| `result` | jsonb | Required | Tool output (JSON) |
| `status` | enum | Required, enum['success', 'failure'] | Invocation outcome |
| `timestamp` | datetime | Required, default now | Invocation timestamp |

**Relationships**:
- Belongs to `Message` (N:1)

**Validation Rules**:
- `tool_name` must be one of: 'create_todo', 'read_todos', 'update_todo', 'delete_todo'
- `parameters` must be valid JSON
- `result` must be valid JSON
- `status` must be 'success' or 'failure'
- `message_id` must reference an 'assistant' role message

**Immutability**:
- All fields are immutable (audit trail)

**Indexes**:
- `(message_id, timestamp)` — retrieve tool invocations for a message
- `(tool_name, timestamp)` — audit queries by tool

**Example (Success)**:
```json
{
  "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "message_id": "a1b2c3d4-5e6f-7a8b-9c0d-e1f2a3b4c5d6",
  "tool_name": "create_todo",
  "parameters": {
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "medium"
  },
  "result": {
    "success": true,
    "todo": {
      "id": "c8d9e0f1-a2b3-4c5d-6e7f-8a9b0c1d2e3f",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "open",
      "priority": "medium",
      "created_at": "2026-01-02T10:01:30Z"
    },
    "error": null
  },
  "status": "success",
  "timestamp": "2026-01-02T10:01:30Z"
}
```

**Example (Failure)**:
```json
{
  "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6b",
  "message_id": "a1b2c3d4-5e6f-7a8b-9c0d-e1f2a3b4c5d7",
  "tool_name": "delete_todo",
  "parameters": {
    "id": "nonexistent-id"
  },
  "result": {
    "success": false,
    "deleted_id": null,
    "error": "Todo not found"
  },
  "status": "failure",
  "timestamp": "2026-01-02T10:02:00Z"
}
```

---

## Relationships Diagram

```
Conversation (1)
    │
    ├──────────────────── (1:N) ──────────────── Message (N)
    │                                                │
    │                                                │
    │                                                ├── (1:N) ──── ToolInvocation (N)
    │                                                │
    │                                                │
    └──────────────────── (0:N) ──────────────── Todo (N)
                          (optional FK)
                          created_in_conversation_id

Conversation
    user_id ────────────────► User (implicit, not stored)

Todo
    user_id ────────────────► User (implicit, not stored)
```

## Query Patterns

### Pattern 1: Load Conversation with Full History
```sql
SELECT c.*, m.*
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.id = ?
ORDER BY m.timestamp ASC
```
**Purpose**: Retrieve all context needed for agent (used per request in stateless design)

---

### Pattern 2: List Todos for User
```sql
SELECT *
FROM todos
WHERE user_id = ?
  AND status != 'archived'
ORDER BY updated_at DESC
```
**Purpose**: Agent retrieves current todos when user asks "Show my todos"

---

### Pattern 3: Get Audit Trail for Message
```sql
SELECT *
FROM tool_invocations
WHERE message_id = ?
ORDER BY timestamp ASC
```
**Purpose**: Retrieve all tool calls made while generating a response

---

### Pattern 4: Get Todo with Audit History
```sql
SELECT t.*, ti.*
FROM todos t
LEFT JOIN tool_invocations ti ON t.id = (ti.result->>'todo'->>'id')
WHERE t.id = ?
ORDER BY ti.timestamp ASC
```
**Purpose**: Track how a specific todo was modified over time

---

## Migration Strategy

### Initial Schema Creation
- Alembic migration: Create 4 tables (Conversation, Message, Todo, ToolInvocation)
- Create indexes on all foreign keys and query patterns
- Add unique constraints where applicable

### Backward Compatibility
- All schema changes require explicit migration scripts
- No breaking changes to API contracts during MVP
- Future changes (e.g., adding fields) use null-safe defaults

## Soft Delete vs. Hard Delete

**Decision**: Soft-delete for Todos (set status = 'archived'; preserve audit trail)
- **Rationale**: Enables recovery, maintains audit trail, respects data retention
- **Implementation**: Deleted todos are hidden by default (`status != 'archived'`) but recoverable

**Exception**: Messages and ToolInvocations are immutable; no deletion (audit trail)

## Data Retention

- **Conversations**: Keep forever (audit trail)
- **Messages**: Keep forever (audit trail)
- **Todos**: Keep forever (audit trail, but soft-delete hides them)
- **ToolInvocations**: Keep forever (audit trail)

**Note**: Retention policy can be updated post-MVP based on compliance requirements.
