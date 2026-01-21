# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `001-ai-todo-chatbot` | **Date**: 2026-01-02 | **Spec**: [./spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-todo-chatbot/spec.md`

## Summary

Build a stateless REST API chatbot using FastAPI that manages todos via natural language. The OpenAI Agents SDK processes user input, invokes MCP tools for todo operations (persisted in PostgreSQL via SQLModel), and returns conversational responses. Conversation history is stored for context retrieval across sessions. All state lives in the database; the server is stateless and horizontally scalable.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, pydantic (SQLModel), asyncpg, MCP SDK
**Storage**: PostgreSQL (via SQLModel ORM)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux server (containerized)
**Project Type**: Web API backend (single service)
**Performance Goals**: <3 second end-to-end latency (per spec SC-001/SC-002); support 100+ todos per conversation without degradation
**Constraints**: <200ms MCP tool invocation latency; <1 second conversation retrieval (per spec SC-007)
**Scale/Scope**: MVP single-user, 5 todo operations (create/read/update/delete/list), <1000 lines of core logic

## Constitution Check

**Gate Status**: ✅ PASS (all principles aligned)

| Principle | Requirement | Plan Alignment |
|-----------|-------------|-----------------|
| I. Stateless Architecture | No in-memory state; database is source of truth | ✅ FastAPI endpoint is stateless; PostgreSQL holds all state (conversations, todos). Each request reads full context from DB. |
| II. Spec-Driven Development | Formal Specify → Plan → Tasks → Implement workflow | ✅ Plan created after spec approval. No manual coding; tasks will be generated from this plan. |
| III. MCP-First Tool Integration | All operations via MCP tools; no hardcoded APIs | ✅ Agent invokes MCP tools for all todo operations. MCP server is separate component with defined contracts. |
| IV. Agent SDK Compliance | Agents stateless; logic in tools or DB | ✅ OpenAI Agents SDK used; agent is ephemeral per-request. Tool implementations are pure functions. |
| V. Database-Driven State | All mutable state in database | ✅ Conversations, messages, todos, tool invocation logs all persisted in PostgreSQL. No runtime state. |
| VI. Test-First Implementation | Tests before code; TDD enforced | ✅ Contract and integration tests will be written before implementation. |
| VII. Simplicity Over Abstraction | Start simple; no premature abstraction | ✅ Single FastAPI service, single MCP server, single SQLModel schema. No repository pattern, no dependency injection framework, no event buses yet. |

**Post-Design Re-check**: All principles remain satisfied.

## Project Structure

### Documentation (this feature)

```
specs/001-ai-todo-chatbot/
├── plan.md              # This file
├── spec.md              # Feature specification (approved)
├── research.md          # (Not needed; tech stack provided)
├── data-model.md        # Entity schemas and relationships
├── quickstart.md        # Developer setup and first run
├── contracts/           # MCP tool contracts and API schemas
│   ├── mcp-tools.md     # MCP tool definitions
│   └── api-schema.md    # REST API OpenAPI spec
└── checklists/
    └── requirements.md  # Quality validation (approved)
```

### Source Code (repository root)

```
src/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, chat endpoint
│   └── routes/
│       └── chat.py          # POST /chat/messages endpoint
├── services/
│   ├── __init__.py
│   ├── agent.py             # OpenAI Agents SDK wrapper
│   ├── mcp_client.py        # MCP tool invocation layer
│   └── todo_manager.py      # Todo CRUD via MCP (business logic)
├── models/
│   ├── __init__.py
│   ├── database.py          # SQLModel schema definitions
│   └── schemas.py           # Pydantic request/response schemas
├── db/
│   ├── __init__.py
│   ├── connection.py        # PostgreSQL connection pool
│   └── migrations/          # Alembic migrations
└── utils/
    ├── __init__.py
    ├── logging.py           # Structured logging
    └── errors.py            # Error handling & translation

tests/
├── contract/
│   └── test_mcp_tools.py    # MCP tool contract validation
├── integration/
│   ├── test_chat_endpoint.py   # Full user journeys
│   └── test_conversation_persistence.py
└── unit/
    ├── test_agent.py
    ├── test_todo_manager.py
    └── test_mcp_client.py

docker/
├── Dockerfile               # Application container
└── docker-compose.yml       # PostgreSQL + app stack

.env.example
requirements.txt
```

**Structure Decision**: Single service architecture (src/ with api/, services/, models/, db/). No frontend; API-only for MVP. Separates concerns: API layer (routes), service layer (agent + MCP orchestration), model layer (database), utilities (logging, errors).

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ Client (HTTP)                                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    POST /chat/messages
                    {conversation_id, message}
                           │
        ┌──────────────────▼───────────────────┐
        │ FastAPI Application (src/api/)       │
        │ - Stateless request handler          │
        │ - Load conversation context from DB  │
        │ - Format agent input                 │
        └──────────────────┬───────────────────┘
                           │
        ┌──────────────────▼───────────────────────┐
        │ Agent Service (src/services/agent.py)    │
        │ - OpenAI Agents SDK wrapper             │
        │ - Processes user message                │
        │ - Invokes MCP tools                     │
        │ - Returns natural language response     │
        └──────────────────┬───────────────────────┘
                           │
        ┌──────────────────▼──────────────────────────────┐
        │ MCP Tool Client (src/services/mcp_client.py)    │
        │ - Discovers available tools                    │
        │ - Invokes tools by name with parameters        │
        │ - Translates tool responses to agent format    │
        │ - Logs all invocations                         │
        └──────────────────┬──────────────────────────────┘
                           │
        ┌──────────────────▼──────────────────────────────┐
        │ MCP Server Process (separate executable)        │
        │ - Tool 1: create_todo(title, desc, priority)  │
        │ - Tool 2: read_todos(filters)                  │
        │ - Tool 3: update_todo(id, fields)             │
        │ - Tool 4: delete_todo(id)                      │
        │ - Each tool calls Todo Manager for DB ops     │
        └──────────────────┬──────────────────────────────┘
                           │
        ┌──────────────────▼──────────────────────────────┐
        │ Todo Manager (src/services/todo_manager.py)     │
        │ - Implements CRUD logic for todos              │
        │ - Validates todo state                         │
        │ - Handles concurrent updates                   │
        │ - Persists to PostgreSQL                       │
        └──────────────────┬──────────────────────────────┘
                           │
        ┌──────────────────▼──────────────────────────────┐
        │ PostgreSQL Database                             │
        │ - Conversations table                          │
        │ - Messages table                               │
        │ - Todos table                                  │
        │ - ToolInvocations table (audit log)           │
        └──────────────────────────────────────────────────┘

        ┌──────────────────────────────────────────────────┐
        │ Response Flow (return to client)                 │
        │ 1. Agent returns response + tool results       │
        │ 2. FastAPI persists message + tool invocations │
        │ 3. Client receives: {response, conversation}   │
        └──────────────────────────────────────────────────┘
```

### Request/Response Flow

**Stateless Chat Endpoint** (`POST /chat/messages`):

```
Input: {
  conversation_id: UUID (or null for new),
  message: string,
  user_id: string (from auth header)
}

Processing:
1. Validate request
2. Retrieve conversation by ID from DB (if exists)
3. Load all prior messages for context
4. Format context for agent: [prior_messages + new_message]
5. Invoke OpenAI Agents SDK
   ├─ Agent receives context
   ├─ Agent determines intent (create/read/update/delete todo)
   ├─ Agent asks MCP tool to execute
   ├─ MCP tool returns result
   ├─ Agent incorporates result into response
6. Persist new message to Conversations.messages
7. Persist tool invocation to ToolInvocations (audit)
8. Return response

Output: {
  conversation_id: UUID,
  message_id: UUID,
  response: string (agent's natural language reply),
  todos: [array of current todos],
  tool_invocations: [audit trail of this request],
  metadata: {timestamp, message_count}
}
```

### MCP Tool Contracts

**Tool 1: create_todo**
```
Input: {
  title: string (required),
  description: string (optional),
  priority: enum[low, medium, high] (default: medium)
}
Output: {
  success: boolean,
  todo: {
    id: UUID,
    title: string,
    description: string,
    status: string (open),
    priority: string,
    created_at: ISO8601
  } | null,
  error: string | null
}
Persists: Todo record to database
Audit: Logged with timestamp, tool_name, parameters, result
```

**Tool 2: read_todos**
```
Input: {
  conversation_id: UUID (optional, filters to this conversation only)
}
Output: {
  todos: [
    {
      id: UUID,
      title: string,
      description: string,
      status: enum[open, completed, archived],
      priority: enum[low, medium, high],
      created_at: ISO8601,
      updated_at: ISO8601
    }
  ],
  count: number,
  error: string | null
}
Persists: None (read-only)
Audit: Logged with timestamp, tool_name, parameters, result
```

**Tool 3: update_todo**
```
Input: {
  id: UUID (required),
  title: string (optional),
  description: string (optional),
  status: enum[open, completed, archived] (optional),
  priority: enum[low, medium, high] (optional)
}
Output: {
  success: boolean,
  todo: {
    id: UUID,
    title: string,
    description: string,
    status: enum[open, completed, archived],
    priority: enum[low, medium, high],
    updated_at: ISO8601
  } | null,
  error: string | null
}
Persists: Updated Todo record
Audit: Logged with timestamp, old_values, new_values, result
```

**Tool 4: delete_todo**
```
Input: {
  id: UUID (required)
}
Output: {
  success: boolean,
  deleted_id: UUID | null,
  error: string | null
}
Persists: Soft-delete or hard-delete of Todo record
Audit: Logged with timestamp, deleted_id, result
```

### MCP Server Responsibilities

1. **Tool Discovery**: Expose list of 4 available tools with signatures to agent
2. **Tool Execution**: Receive tool requests from agent, validate parameters, execute
3. **Database Persistence**: Delegate to Todo Manager for actual CRUD
4. **Error Translation**: Convert database errors to user-friendly error responses
5. **Logging**: Log all tool invocations for audit trail
6. **Contract Compliance**: Ensure all responses match declared schemas

### Agent Execution Flow (Per Request)

```
Request arrives at FastAPI endpoint
    ↓
Load conversation history from PostgreSQL
    ↓
Format context:
  system_prompt: "You are a helpful todo assistant. Help users manage their todos..."
  prior_messages: [all prior user/assistant messages]
  current_user_message: "Create a todo to buy groceries"
    ↓
Invoke OpenAI Agents SDK with context
    ↓
Agent (LLM) reads context and determines:
  "User wants to CREATE a todo with title 'buy groceries'"
    ↓
Agent constructs tool call:
  tool_name: "create_todo"
  parameters: {title: "buy groceries", priority: "medium"}
    ↓
FastAPI catches tool call, routes to MCP client
    ↓
MCP client invokes MCP server tool
    ↓
MCP server:
  1. Validates parameters
  2. Calls Todo Manager
  3. Todo Manager persists to PostgreSQL
  4. Returns result: {success: true, todo: {...}}
    ↓
Agent receives result, generates response:
  "I've created a todo to buy groceries for you!"
    ↓
FastAPI persists:
  1. Message record (role: assistant, content: "I've created...")
  2. ToolInvocation record (tool_name, parameters, result)
    ↓
Client receives response with current todo state
```

### Database Interactions

**Conversation Schema**:
```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: str  # From auth header
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Relationship: messages
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Message Schema**:
```python
class Message(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    conversation_id: UUID = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str  # Full message text
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # Relationship: conversation, tool_invocations
    conversation: Conversation = Relationship(back_populates="messages")
    tool_invocations: List["ToolInvocation"] = Relationship(back_populates="message")
```

**Todo Schema**:
```python
class Todo(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: str  # From auth header (for multi-user future)
    title: str  # Required
    description: Optional[str] = None
    status: str = "open"  # open, completed, archived
    priority: str = "medium"  # low, medium, high
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_in_conversation_id: Optional[UUID] = None  # Reference to originating conversation
```

**ToolInvocation Schema** (audit log):
```python
class ToolInvocation(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    message_id: UUID = Field(foreign_key="message.id")
    tool_name: str  # e.g., "create_todo"
    parameters: dict  # JSON blob of input parameters
    result: dict  # JSON blob of tool output
    status: str  # "success" or "failure"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # Relationship: message
    message: Message = Relationship(back_populates="tool_invocations")
```

**Query Patterns**:
- Get conversation with all messages: `SELECT * FROM conversations WHERE id = ? JOIN messages`
- Get todos for conversation: `SELECT * FROM todos WHERE created_in_conversation_id = ?`
- Get todos for user: `SELECT * FROM todos WHERE user_id = ? ORDER BY updated_at DESC`
- Get tool invocations for message: `SELECT * FROM tool_invocations WHERE message_id = ?`
- Retrieve conversation history: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC`

### Error Handling

**Tool Failures**:
- Tool returns `{success: false, error: "..."}`
- Agent receives error and generates user-friendly response: "Sorry, I couldn't create the todo. [reason]"
- ToolInvocation logged with status: "failure"

**Ambiguous Input**:
- Agent recognizes ambiguity ("Mark todo as done" when 5 todos are open)
- Agent asks clarifying question: "I found 5 open todos. Which one should I mark as complete?"
- No tool is invoked; conversation continues

**Database Unavailable**:
- Connection pool returns error
- FastAPI catches, returns: `{status: 503, message: "Temporarily unavailable"}`
- Client should retry or inform user

**Invalid Tool Parameters**:
- MCP server validates parameters against schema
- Returns: `{success: false, error: "Invalid priority: 'urgent'"}`
- Agent recovers by asking user for valid input

## Complexity Justification

| Aspect | Approach | Justification |
|--------|----------|---------------|
| Stateless architecture | All state in PostgreSQL; FastAPI is stateless | Required by constitution; enables horizontal scaling and simplifies testing. No in-memory caches. |
| MCP tools as facade | All todo operations via MCP tools, not direct FastAPI service logic | Required by constitution (MCP-First). Decouples agent from todo operations; enables reuse by other systems. |
| Conversation persistence | Full message history stored; context loaded for each request | Required by spec (US2). Supports resuming conversations across sessions. No caching; always load from DB. |
| OpenAI Agents SDK | Single agent instance per request, ephemeral | Required by constitution (Agent SDK compliance). Stateless design; no agent state between requests. |
| Single service | No separate todo API; MCP tools own CRUD | Simpler than microservices for MVP. All logic co-located. If scale demands separation, create separate todo service and update MCP client to call it. |

## Next Steps (Phase 2: Tasks)

After approval of this plan:
1. `/sp.tasks` will generate testable task list from this design
2. Tasks will follow test-first TDD cycle (red → green → refactor)
3. Implementation tasks for: database schema, FastAPI endpoints, MCP server, agent integration, tests

## References

- **Specification**: ./spec.md
- **Constitution**: ../../.specify/memory/constitution.md
- **OpenAI Agents SDK**: https://platform.openai.com/docs/guides/agents
- **MCP Protocol**: https://modelcontextprotocol.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **PostgreSQL**: https://www.postgresql.org/
