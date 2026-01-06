# API Documentation (T086)

## Overview

The AI-Powered Todo Chatbot API provides a single HTTP endpoint for natural language todo management. Users send messages and receive agent responses along with current todo state.

## Base URL

```
POST http://localhost:8000
```

## Authentication

All requests require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <JWT_TOKEN>
```

The JWT token must contain a `sub` claim with the user ID.

## Endpoints

### POST /chat/messages

Process a user message and return agent response.

**Request**:

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Create a todo to buy groceries"
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | UUID | No | Existing conversation ID; if omitted, creates new conversation |
| message | string | Yes | User message; cannot be empty |

**Response** (200 OK):

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "response": "I've created a todo 'Buy groceries' for you!",
  "todos": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "user_id": "user-123",
      "title": "Buy groceries",
      "description": null,
      "status": "open",
      "priority": "medium",
      "created_at": "2026-01-04T10:30:00Z",
      "updated_at": "2026-01-04T10:30:00Z",
      "created_in_conversation_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "tool_invocations": [
    {
      "tool_name": "create_todo",
      "parameters": "{\"title\": \"Buy groceries\", \"priority\": \"medium\"}",
      "result": "{\"success\": true, \"todo\": {...}}",
      "status": "success",
      "timestamp": "2026-01-04T10:30:00Z"
    }
  ],
  "metadata": {
    "timestamp": "2026-01-04T10:30:00Z",
    "message_count": 1
  }
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | UUID | Conversation ID (existing or newly created) |
| message_id | UUID | ID of the assistant's response message |
| response | string | Agent's natural language response |
| todos | array | Current user todos (excludes archived) |
| tool_invocations | array | List of MCP tools invoked for this request |
| metadata | object | Response metadata (timestamp, message_count) |

**Error Responses**:

| Status | Description | Example |
|--------|-------------|---------|
| 400 Bad Request | Empty message or invalid conversation_id | `{"detail": "Message cannot be empty"}` |
| 401 Unauthorized | Missing or invalid JWT token | `{"detail": "Not authenticated"}` |
| 403 Forbidden | User attempting to access other user's conversation | `{"detail": "Access denied"}` |
| 404 Not Found | Conversation ID doesn't exist | `{"detail": "Conversation not found"}` |
| 500 Internal Server Error | Unexpected error | `{"detail": "Failed to process message"}` |
| 503 Service Unavailable | Database unavailable | `{"detail": "Temporarily unavailable"}` |

## Examples

### Create a Todo

**Request**:
```bash
curl -X POST http://localhost:8000/chat/messages \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a todo to call mom"
  }'
```

**Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "response": "I've created a todo 'Call mom' for you!",
  "todos": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "title": "Call mom",
      "status": "open",
      "priority": "medium"
    }
  ],
  "tool_invocations": [...],
  "metadata": {
    "timestamp": "2026-01-04T10:30:00Z",
    "message_count": 1
  }
}
```

### List Todos

**Request**:
```bash
curl -X POST http://localhost:8000/chat/messages \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Show my todos"
  }'
```

**Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "response": "Here are your todos:\n- Call mom (open)\n- Buy groceries (open)",
  "todos": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "title": "Call mom",
      "status": "open",
      "priority": "medium"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440003",
      "title": "Buy groceries",
      "status": "open",
      "priority": "medium"
    }
  ],
  "tool_invocations": [...],
  "metadata": {
    "timestamp": "2026-01-04T10:30:00Z",
    "message_count": 2
  }
}
```

### Resume Conversation

**Request**:
```bash
curl -X POST http://localhost:8000/chat/messages \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Mark the first one as done"
  }'
```

The agent will use prior conversation context to understand "the first one" refers to "Call mom".

## Performance Targets

Based on spec SC-001, SC-002, SC-003:

| Operation | Target Latency |
|-----------|----------------|
| Create todo | <3 seconds |
| List todos (100 items) | <2 seconds |
| Conversation retrieval | <1 second |

See `tests/integration/test_performance.py` for latency tests.

## Rate Limiting

No rate limiting implemented in MVP. Consider adding for production.

## Security

- **JWT Authentication**: All requests require valid JWT token
- **User Isolation**: Users can only access their own conversations and todos
- **Input Validation**: Empty messages rejected with 400 Bad Request
- **Error Messages**: Technical errors not exposed to users
- **Access Control**: 403 Forbidden for cross-user access attempts

## Support

For issues or questions, refer to:
- `docs/setup.md` - Setup and troubleshooting
- `docs/mcp-tools.md` - MCP tool documentation
- `specs/001-ai-todo-chatbot/spec.md` - Feature specification
