# API Schema: AI-Powered Todo Chatbot

**Feature**: AI-Powered Todo Chatbot
**Created**: 2026-01-02
**Type**: REST API (OpenAPI 3.0.0)

## Overview

Single stateless endpoint for chatbot interaction. All state (conversation history, todos) is stored in the database and returned in responses. Clients pass full conversation context with each request; server returns updated state.

## Endpoints

### POST /chat/messages

**Purpose**: Send a user message to the chatbot and receive a response.

**Request Headers**:
```
Authorization: Bearer {jwt_token}  # Contains user_id in claims
Content-Type: application/json
```

**Request Body**:
```json
{
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",  // UUID or null for new conversation
  "message": "Create a todo to buy groceries"  // User input text
}
```

**Request Validation**:
- `conversation_id`: UUID format or null (required field, but null means create new)
- `message`: string, non-empty, max 10,000 characters
- Authorization header must contain valid JWT with `user_id` claim

**Response (200 OK)**:
```json
{
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message_id": "a1b2c3d4-5e6f-7a8b-9c0d-e1f2a3b4c5d6",
  "response": "I've created a todo to buy groceries for you!",
  "todos": [
    {
      "id": "c8d9e0f1-a2b3-4c5d-6e7f-8a9b0c1d2e3f",
      "title": "Buy groceries",
      "description": null,
      "status": "open",
      "priority": "medium",
      "created_at": "2026-01-02T10:01:30Z",
      "updated_at": "2026-01-02T10:01:30Z"
    }
  ],
  "tool_invocations": [
    {
      "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
      "tool_name": "create_todo",
      "parameters": {
        "title": "Buy groceries",
        "description": null,
        "priority": "medium"
      },
      "result": {
        "success": true,
        "todo": {
          "id": "c8d9e0f1-a2b3-4c5d-6e7f-8a9b0c1d2e3f",
          "title": "Buy groceries",
          "description": null,
          "status": "open",
          "priority": "medium",
          "created_at": "2026-01-02T10:01:30Z"
        },
        "error": null
      },
      "status": "success",
      "timestamp": "2026-01-02T10:01:30Z"
    }
  ],
  "metadata": {
    "timestamp": "2026-01-02T10:01:30Z",
    "message_count": 2,  // Total messages in conversation
    "processing_time_ms": 450
  }
}
```

**Response Fields**:
- `conversation_id` (UUID): The conversation ID (created if null in request)
- `message_id` (UUID): ID of the agent response message
- `response` (string): Natural language response from chatbot
- `todos` (array): Current state of all user's todos (from `read_todos` MCP tool)
- `tool_invocations` (array): All tool calls made during this request (audit trail)
- `metadata` (object): Request metadata

**Response Errors**:

**400 Bad Request**:
```json
{
  "error": "invalid_request",
  "message": "Message must be non-empty",
  "details": {}
}
```
- Invalid message format
- Invalid conversation_id format
- Message exceeds max length

**401 Unauthorized**:
```json
{
  "error": "unauthorized",
  "message": "Missing or invalid authorization token"
}
```
- Missing Authorization header
- Invalid JWT token
- Expired token

**404 Not Found**:
```json
{
  "error": "conversation_not_found",
  "message": "Conversation f47ac10b-58cc-4372-a567-0e02b2c3d479 does not exist or is not owned by this user"
}
```
- `conversation_id` references non-existent conversation
- User attempting to access conversation they don't own

**500 Internal Server Error**:
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred. Please try again later.",
  "request_id": "req-12345-abcde"  // For debugging
}
```
- Database connection failure
- Unexpected agent error
- Unhandled exception

**503 Service Unavailable**:
```json
{
  "error": "service_unavailable",
  "message": "Temporarily unable to process requests. Please try again in a moment."
}
```
- Database temporarily unavailable
- MCP server down
- Rate limited

---

## Response Latency Targets

Per specification success criteria:
- **Create todo**: <3 seconds (SC-001)
- **List todos**: <2 seconds (SC-002)
- **Error latency**: <1 second (SC-007)
- **Conversation retrieval**: <1 second (SC-007)

---

## Request/Response Examples

### Example 1: Create Todo

**Request**:
```bash
curl -X POST http://localhost:8000/chat/messages \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": null,
    "message": "Create a todo: finish project report by Friday"
  }'
```

**Response** (200 OK):
```json
{
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message_id": "msg-001",
  "response": "I've created a todo 'finish project report by Friday' for you. I've marked it as high priority since you mentioned a deadline.",
  "todos": [
    {
      "id": "todo-001",
      "title": "finish project report by Friday",
      "description": null,
      "status": "open",
      "priority": "high",
      "created_at": "2026-01-02T10:00:00Z",
      "updated_at": "2026-01-02T10:00:00Z"
    }
  ],
  "tool_invocations": [
    {
      "id": "inv-001",
      "tool_name": "create_todo",
      "parameters": {
        "title": "finish project report by Friday",
        "priority": "high"
      },
      "result": {
        "success": true,
        "todo": {...},
        "error": null
      },
      "status": "success",
      "timestamp": "2026-01-02T10:00:00Z"
    }
  ],
  "metadata": {
    "timestamp": "2026-01-02T10:00:00Z",
    "message_count": 1,
    "processing_time_ms": 850
  }
}
```

---

### Example 2: Resume Conversation and List Todos

**Request**:
```bash
curl -X POST http://localhost:8000/chat/messages \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "message": "Show me all my todos"
  }'
```

**Response** (200 OK):
```json
{
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message_id": "msg-002",
  "response": "Here are all your current todos:\n1. finish project report by Friday (high priority, open)\n2. buy groceries (medium priority, open)\n\nYou have 2 open todos.",
  "todos": [
    {
      "id": "todo-001",
      "title": "finish project report by Friday",
      "status": "open",
      "priority": "high",
      "created_at": "2026-01-02T10:00:00Z",
      "updated_at": "2026-01-02T10:00:00Z"
    },
    {
      "id": "todo-002",
      "title": "buy groceries",
      "status": "open",
      "priority": "medium",
      "created_at": "2026-01-02T10:01:00Z",
      "updated_at": "2026-01-02T10:01:00Z"
    }
  ],
  "tool_invocations": [
    {
      "id": "inv-002",
      "tool_name": "read_todos",
      "parameters": {},
      "result": {
        "todos": [...],
        "count": 2,
        "error": null
      },
      "status": "success",
      "timestamp": "2026-01-02T10:02:00Z"
    }
  ],
  "metadata": {
    "timestamp": "2026-01-02T10:02:00Z",
    "message_count": 2,
    "processing_time_ms": 450
  }
}
```

---

### Example 3: Error Case - Tool Failure

**Request**:
```bash
curl -X POST http://localhost:8000/chat/messages \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "message": "Mark the project todo as done"
  }'
```

**Response** (200 OK, with tool failure):
```json
{
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message_id": "msg-003",
  "response": "I found your project todo. Let me mark it as complete for you... Done! I've marked 'finish project report by Friday' as completed.",
  "todos": [
    {
      "id": "todo-001",
      "title": "finish project report by Friday",
      "status": "completed",  // Status changed
      "priority": "high",
      "created_at": "2026-01-02T10:00:00Z",
      "updated_at": "2026-01-02T10:03:00Z"
    },
    {
      "id": "todo-002",
      "title": "buy groceries",
      "status": "open",
      "priority": "medium",
      "created_at": "2026-01-02T10:01:00Z",
      "updated_at": "2026-01-02T10:01:00Z"
    }
  ],
  "tool_invocations": [
    {
      "id": "inv-003",
      "tool_name": "update_todo",
      "parameters": {
        "id": "todo-001",
        "status": "completed"
      },
      "result": {
        "success": true,
        "todo": {
          "id": "todo-001",
          "status": "completed",
          "updated_at": "2026-01-02T10:03:00Z"
        },
        "error": null
      },
      "status": "success",
      "timestamp": "2026-01-02T10:03:00Z"
    }
  ],
  "metadata": {
    "timestamp": "2026-01-02T10:03:00Z",
    "message_count": 3,
    "processing_time_ms": 580
  }
}
```

---

## API Constraints and Notes

1. **Stateless Design**: Server maintains no state between requests. All conversation context is loaded from database and returned in response.

2. **User Isolation**: Each request is validated to ensure user_id from JWT matches conversation ownership. Users cannot access other users' conversations.

3. **Rate Limiting** (not in MVP, but placeholder for future):
   - Plan: 100 requests per user per minute
   - Implement via API gateway or FastAPI middleware

4. **Pagination** (not in MVP; conversations are individual threads):
   - If future feature requires listing conversations, pagination will be added

5. **Idempotency**: Requests are NOT idempotent (same message twice = two separate exchanges). If idempotency needed, client should include `idempotency-key` header (future enhancement).

6. **Versioning**: No explicit API versioning yet. If breaking changes needed post-MVP, use `/v2/chat/messages` endpoint.

---

## OpenAPI 3.0.0 Specification

```yaml
openapi: 3.0.0
info:
  title: AI-Powered Todo Chatbot API
  description: Stateless REST API for managing todos via conversational interface
  version: 1.0.0

servers:
  - url: http://localhost:8000
    description: Local development
  - url: https://api.example.com
    description: Production

paths:
  /chat/messages:
    post:
      summary: Send message to chatbot
      description: Stateless endpoint that processes user message and returns agent response with current todo state
      operationId: chatMessages
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - conversation_id
                - message
              properties:
                conversation_id:
                  type: string
                  format: uuid
                  nullable: true
                  description: UUID of conversation (null for new conversation)
                message:
                  type: string
                  minLength: 1
                  maxLength: 10000
                  description: User message text
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'
        '400':
          description: Bad request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '404':
          description: Conversation not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '503':
          description: Service unavailable
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
      security:
        - BearerAuth: []

components:
  schemas:
    ChatResponse:
      type: object
      required:
        - conversation_id
        - message_id
        - response
        - todos
        - tool_invocations
        - metadata
      properties:
        conversation_id:
          type: string
          format: uuid
        message_id:
          type: string
          format: uuid
        response:
          type: string
        todos:
          type: array
          items:
            $ref: '#/components/schemas/Todo'
        tool_invocations:
          type: array
          items:
            $ref: '#/components/schemas/ToolInvocation'
        metadata:
          $ref: '#/components/schemas/Metadata'

    Todo:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
        description:
          type: string
          nullable: true
        status:
          type: string
          enum: [open, completed, archived]
        priority:
          type: string
          enum: [low, medium, high]
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    ToolInvocation:
      type: object
      properties:
        id:
          type: string
          format: uuid
        tool_name:
          type: string
          enum: [create_todo, read_todos, update_todo, delete_todo]
        parameters:
          type: object
        result:
          type: object
        status:
          type: string
          enum: [success, failure]
        timestamp:
          type: string
          format: date-time

    Metadata:
      type: object
      properties:
        timestamp:
          type: string
          format: date-time
        message_count:
          type: integer
        processing_time_ms:
          type: integer

    ErrorResponse:
      type: object
      required:
        - error
        - message
      properties:
        error:
          type: string
        message:
          type: string
        details:
          type: object

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

## Implementation Notes

1. **Response Serialization**: All responses use ISO8601 timestamps and UUID strings
2. **JSON Nullability**: Optional fields are included with `null` value (not omitted)
3. **Tool Parameters/Result**: Stored as JSON; no schema validation on outer level (flexibility for tool updates)
4. **HTTP Status Codes**: Only 200 OK for successful requests; error responses use appropriate 4xx/5xx codes
