# MCP Tool Documentation (T087)

## Overview

The AI-Powered Todo Chatbot uses Model Context Protocol (MCP) tools to perform todo management operations. These tools are invoked by the agent based on user intent.

## Available Tools

### 1. create_todo

Create a new todo item.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | Todo title (max 255 chars) |
| description | string | No | Todo description |
| priority | enum | No | Priority level: "low", "medium", "high" (default: "medium") |

**Request Example**:

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "medium"
}
```

**Response**:

```json
{
  "success": true,
  "error": null,
  "todo": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user_id": "user-123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "open",
    "priority": "medium",
    "created_at": "2026-01-04T10:30:00Z",
    "updated_at": "2026-01-04T10:30:00Z"
  }
}
```

**Error Cases**:

- Empty title → `{"success": false, "error": "Title cannot be empty"}`
- Database error → `{"success": false, "error": "Failed to create todo"}`

---

### 2. read_todos

List all todos for the current user.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | enum | No | Filter by status: "open", "completed", "archived" (default: all non-archived) |
| limit | integer | No | Max results to return (default: 100) |
| offset | integer | No | Result offset for pagination (default: 0) |

**Request Example**:

```json
{
  "status": "open"
}
```

**Response**:

```json
{
  "success": true,
  "error": null,
  "todos": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "user_id": "user-123",
      "title": "Buy groceries",
      "status": "open",
      "priority": "medium",
      "created_at": "2026-01-04T10:30:00Z",
      "updated_at": "2026-01-04T10:30:00Z"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440003",
      "user_id": "user-123",
      "title": "Call mom",
      "status": "open",
      "priority": "high",
      "created_at": "2026-01-04T10:25:00Z",
      "updated_at": "2026-01-04T10:25:00Z"
    }
  ],
  "count": 2
}
```

**Error Cases**:

- Database error → `{"success": false, "error": "Failed to read todos"}`

---

### 3. update_todo

Update an existing todo item.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Todo ID to update |
| title | string | No | New todo title |
| description | string | No | New todo description |
| status | enum | No | New status: "open", "completed", "archived" |
| priority | enum | No | New priority: "low", "medium", "high" |

**Request Example**:

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "completed",
  "priority": "low"
}
```

**Response**:

```json
{
  "success": true,
  "error": null,
  "todo": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user_id": "user-123",
    "title": "Buy groceries",
    "status": "completed",
    "priority": "low",
    "created_at": "2026-01-04T10:30:00Z",
    "updated_at": "2026-01-04T11:45:00Z"
  }
}
```

**Error Cases**:

- Todo not found → `{"success": false, "error": "Todo not found"}`
- Empty title → `{"success": false, "error": "Title cannot be empty"}`
- Unauthorized access → `{"success": false, "error": "Access denied"}`

---

### 4. delete_todo

Delete (archive) a todo item. This is a soft delete - todos are marked as "archived", not permanently removed.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Todo ID to delete |

**Request Example**:

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002"
}
```

**Response**:

```json
{
  "success": true,
  "error": null,
  "deleted_id": "770e8400-e29b-41d4-a716-446655440002"
}
```

**Error Cases**:

- Todo not found → `{"success": false, "error": "Todo not found"}`
- Unauthorized access → `{"success": false, "error": "Access denied"}`

---

## Tool Contract Schema

All MCP tool responses follow this schema:

```json
{
  "success": boolean,
  "error": string | null,
  "data": any,
  "user_message": string
}
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether operation succeeded |
| error | string \| null | Error message if operation failed |
| data | any | Tool-specific response data |
| user_message | string | User-friendly message for agent to return |

---

## Agent Tool Invocation

The agent invokes tools based on user intent:

| User Intent | Tool Called | Example |
|-------------|-------------|---------|
| "Create a todo..." | create_todo | "Create a todo to buy milk" |
| "Show my todos", "List todos" | read_todos | "What are my todos?" |
| "Mark as done", "Complete", "Archive" | update_todo | "Mark the first one as complete" |
| "Delete", "Remove" | delete_todo | "Delete the oldest todo" |

---

## Tool Invocation Logging

All tool invocations are logged to the `ToolInvocation` table with:

- message_id: ID of the assistant message that invoked the tool
- tool_name: Name of the tool invoked
- parameters: Input parameters (JSON)
- result: Tool output (JSON)
- status: "success" or "failure"
- timestamp: When the invocation occurred

This enables audit trails and debugging.

---

## Error Handling

When a tool fails:

1. **Tool returns error result**: `{"success": false, "error": "error message"}`
2. **MCP client logs failure**: Invocation logged with status="failure"
3. **Agent translates error**: Error message converted to user-friendly text
4. **User receives friendly message**: e.g., "I'm having trouble updating that todo. Please try again."

See `src/utils/errors.py` for error translation logic.

---

## Performance Targets

Tool invocation latencies (per spec SC-001):

| Operation | Target |
|-----------|--------|
| create_todo | <3 seconds total |
| read_todos (100 items) | <2 seconds |
| update_todo | <3 seconds total |
| delete_todo | <3 seconds total |

Tool invocation timeout: 5 seconds (enforced in `src/services/mcp_client.py`)

---

## Security

- **User Isolation**: All tools filter by `user_id` - users cannot access other users' todos
- **Validation**: Tool parameters validated before execution
- **Immutability**: Created/updated timestamps immutable after creation
- **Soft Delete**: No data permanently removed - todos marked as "archived"

---

## References

- API Contract: `specs/001-ai-todo-chatbot/contracts/mcp-tools.md`
- Implementation: `src/services/mcp_client.py`
- MCP Server: `src/mcp_server.py`
- Tool Manager: `src/services/todo_manager.py`
