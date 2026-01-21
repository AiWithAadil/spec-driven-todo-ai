# MCP Tool Contracts: AI-Powered Todo Chatbot

**Feature**: AI-Powered Todo Chatbot
**Created**: 2026-01-02
**Type**: Model Context Protocol (MCP) Tool Definitions

## Overview

Four MCP tools provide the chatbot agent with todo management capabilities. All tools are invoked by the OpenAI Agents SDK via the MCP protocol. Tools are stateless; all persistence is handled by the Todo Manager service connecting to PostgreSQL.

## Tool Definitions

### Tool 1: create_todo

**Purpose**: Create a new todo with optional description and priority.

**Availability**: Always available

**Parameters**:

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| `title` | string | Yes | Todo title/name | "Buy groceries" |
| `description` | string | No | Detailed description | "Milk, eggs, bread" |
| `priority` | enum | No | Priority level | "medium" |

**Priority Values**: `low`, `medium` (default), `high`

**Success Response**:
```json
{
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
}
```

**Error Response**:
```json
{
  "success": false,
  "todo": null,
  "error": "Title is required and must be non-empty"
}
```

**Possible Errors**:
- `Title is required and must be non-empty` — title field missing or empty
- `Title must be max 200 characters` — title exceeds length limit
- `Description must be max 5000 characters` — description exceeds limit
- `Invalid priority value: {value}` — priority not in [low, medium, high]
- `Database error` — storage failure

**Side Effects**:
- Creates Todo record in database
- Sets status = "open", created_at = now, updated_at = now
- Logs ToolInvocation record

---

### Tool 2: read_todos

**Purpose**: Retrieve all todos for the current user (optionally filtered by conversation).

**Availability**: Always available

**Parameters**:

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| `conversation_id` | UUID string | No | Filter to todos created in this conversation | "f47ac10b-58cc-4372-a567-0e02b2c3d479" |

**Success Response**:
```json
{
  "todos": [
    {
      "id": "c8d9e0f1-a2b3-4c5d-6e7f-8a9b0c1d2e3f",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "open",
      "priority": "medium",
      "created_at": "2026-01-02T10:01:30Z",
      "updated_at": "2026-01-02T10:01:30Z"
    },
    {
      "id": "d9e0f1a2-b3c4-5d6e-7f8a-9b0c1d2e3f4a",
      "title": "Finish project report",
      "description": null,
      "status": "open",
      "priority": "high",
      "created_at": "2026-01-02T10:00:00Z",
      "updated_at": "2026-01-02T10:00:00Z"
    }
  ],
  "count": 2,
  "error": null
}
```

**Error Response**:
```json
{
  "todos": [],
  "count": 0,
  "error": "Invalid conversation_id format"
}
```

**Possible Errors**:
- `Invalid conversation_id format` — conversation_id not a valid UUID
- `Conversation not found` — conversation_id references non-existent conversation
- `Database error` — query failure

**Behavior**:
- Returns all todos with status != "archived" by default
- Returns empty list if user has no todos
- Filters by `conversation_id` if provided
- Orders by updated_at DESC (most recent first)

**Side Effects**:
- None (read-only)
- Logs ToolInvocation record

---

### Tool 3: update_todo

**Purpose**: Update an existing todo's title, description, status, or priority.

**Availability**: Always available

**Parameters**:

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| `id` | UUID string | Yes | Todo ID to update | "c8d9e0f1-a2b3-4c5d-6e7f-8a9b0c1d2e3f" |
| `title` | string | No | New title (if updating) | "Buy groceries and cook dinner" |
| `description` | string | No | New description (if updating) | "Milk, eggs, bread, chicken" |
| `status` | enum | No | New status | "completed" |
| `priority` | enum | No | New priority | "high" |

**Status Values**: `open`, `completed`, `archived`
**Priority Values**: `low`, `medium`, `high`

**Success Response**:
```json
{
  "success": true,
  "todo": {
    "id": "c8d9e0f1-a2b3-4c5d-6e7f-8a9b0c1d2e3f",
    "title": "Buy groceries and cook dinner",
    "description": "Milk, eggs, bread, chicken",
    "status": "completed",
    "priority": "high",
    "updated_at": "2026-01-02T10:02:00Z"
  },
  "error": null
}
```

**Error Response**:
```json
{
  "success": false,
  "todo": null,
  "error": "Todo not found"
}
```

**Possible Errors**:
- `Todo not found` — id references non-existent todo
- `Invalid id format` — id not a valid UUID
- `Title must be max 200 characters` — new title exceeds limit
- `Description must be max 5000 characters` — new description exceeds limit
- `Invalid status value: {value}` — status not in [open, completed, archived]
- `Invalid priority value: {value}` — priority not in [low, medium, high]
- `Database error` — update failure

**Behavior**:
- Only updates provided fields; omitted fields are unchanged
- Sets updated_at = now
- Returns full updated todo object
- No-op if no fields change (still returns success)

**Side Effects**:
- Updates Todo record in database
- Logs ToolInvocation record with old and new values (for audit)

---

### Tool 4: delete_todo

**Purpose**: Delete an existing todo (soft-delete; mark as archived or hard-delete).

**Availability**: Always available

**Parameters**:

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| `id` | UUID string | Yes | Todo ID to delete | "c8d9e0f1-a2b3-4c5d-6e7f-8a9b0c1d2e3f" |

**Success Response** (soft-delete approach):
```json
{
  "success": true,
  "deleted_id": "c8d9e0f1-a2b3-4c5d-6e7f-8a9b0c1d2e3f",
  "error": null
}
```

**Error Response**:
```json
{
  "success": false,
  "deleted_id": null,
  "error": "Todo not found"
}
```

**Possible Errors**:
- `Todo not found` — id references non-existent todo
- `Invalid id format` — id not a valid UUID
- `Todo already deleted` — todo is already archived (duplicate delete)
- `Database error` — deletion failure

**Behavior**:
- Soft-deletes by setting status = "archived" (preserves audit trail)
- Marks updated_at = now
- Returns the deleted todo's ID

**Side Effects**:
- Updates Todo record (status = "archived")
- Logs ToolInvocation record

---

## Tool Invocation Flow (from Agent Perspective)

```
Agent processes user message: "Create a todo to buy groceries"
    ↓
Agent determines intent: CREATE
    ↓
Agent constructs tool call:
  {
    "tool": "create_todo",
    "parameters": {
      "title": "buy groceries",
      "priority": "medium"
    }
  }
    ↓
MCP Client routes to MCP Server
    ↓
MCP Server invokes create_todo tool
    ↓
Tool executes CRUD logic via Todo Manager
    ↓
Tool returns result:
  {
    "success": true,
    "todo": {...},
    "error": null
  }
    ↓
Agent receives result
    ↓
Agent incorporates into response:
  "I've created a todo 'buy groceries' for you with medium priority."
    ↓
FastAPI persists:
  - Message record (role: assistant)
  - ToolInvocation record (audit trail)
    ↓
Response sent to client
```

---

## Error Handling Strategy

### Tool-Level Errors

Tools return structured error responses without raising exceptions:
```json
{
  "success": false,
  "result": null,
  "error": "Clear, human-readable error message"
}
```

### Agent-Level Error Recovery

When a tool returns failure, the agent:
1. Reads the error message
2. Decides whether to retry or ask user for clarification
3. Generates a user-friendly response

Example:
```
Tool returns: {success: false, error: "Title is required"}
Agent responds: "I need more information. What should I title this todo?"
```

### Server-Level Error Handling

If MCP Server crashes or is unavailable:
- FastAPI catches the exception
- Returns 503 Service Unavailable to client
- Logs the error with request ID for debugging
- Agent does not retry automatically (client should retry)

---

## Tool Constraints and Limitations

1. **Single-User Scope**: All tools operate on current user's todos (identified via JWT user_id). No multi-user filtering within tools.

2. **No Transactions Across Tools**: Each tool is atomic. If multiple tools are invoked in sequence (e.g., delete + create), they are separate transactions.

3. **No Pagination**: read_todos returns all todos (MVP constraint). If 100+ todos, all are returned.

4. **No Search/Filter**: read_todos returns all todos. Agent must parse the list to find specific todos by title/description.

5. **No Bulk Operations**: No batch create/update/delete. Agent must invoke tools individually.

6. **No Undo**: Deleted todos (archived) cannot be unarchived by tools (manual DB operation only).

---

## Tool Discoverability

MCP Server exposes tool metadata for agent discovery:

```json
{
  "tools": [
    {
      "name": "create_todo",
      "description": "Create a new todo with optional description and priority",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "Todo title"
          },
          "description": {
            "type": "string",
            "description": "Optional todo description"
          },
          "priority": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "Optional priority level"
          }
        },
        "required": ["title"]
      }
    },
    {
      "name": "read_todos",
      "description": "Retrieve all todos for the current user",
      "parameters": {...}
    },
    {
      "name": "update_todo",
      "description": "Update an existing todo",
      "parameters": {...}
    },
    {
      "name": "delete_todo",
      "description": "Delete (archive) an existing todo",
      "parameters": {...}
    }
  ]
}
```

---

## Performance Characteristics

| Tool | Operation | Target Latency | Notes |
|------|-----------|-----------------|-------|
| create_todo | INSERT | <500ms | Fast; single row write |
| read_todos | SELECT | <1000ms | May slow with 100+ todos; no pagination |
| update_todo | UPDATE | <500ms | Single row update |
| delete_todo | UPDATE (soft-delete) | <500ms | Single row update (status = archived) |

---

## Audit and Logging

Every tool invocation is logged to ToolInvocation table:

```python
ToolInvocation(
  id=uuid4(),
  message_id=current_message_id,
  tool_name="create_todo",
  parameters={"title": "...", "priority": "..."},
  result={"success": true, "todo": {...}, "error": null},
  status="success",  # or "failure"
  timestamp=now()
)
```

This enables:
- **Audit Trail**: Who called what tool, when, with what parameters
- **Debugging**: Replay tool invocations to understand agent behavior
- **Monitoring**: Count successes/failures per tool
- **Testing**: Validate tool contracts by inspecting logs

---

## Future Enhancements (Out of Scope for MVP)

- `search_todos` — Full-text search by title/description
- `list_todos` — Paginated listing
- `archive_bulk` — Batch archive multiple todos
- `create_recurring_todo` — Schedule todos to repeat
- `set_reminder` — Remind user before deadline
- `assign_todo` — Share todo with other user (multi-user feature)
