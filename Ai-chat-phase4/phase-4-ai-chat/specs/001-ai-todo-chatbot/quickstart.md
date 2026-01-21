# Developer Quickstart: AI-Powered Todo Chatbot

**Feature**: AI-Powered Todo Chatbot
**Created**: 2026-01-02
**Status**: Phase 1 Design (Implementation TBD)

## Overview

This guide walks through the architecture, component interactions, and local setup for the AI-powered Todo chatbot. For implementation tasks, refer to `/sp.tasks` output after design approval.

## Architecture at a Glance

```
Client (HTTP)
    ↓ POST /chat/messages
FastAPI App
    ├─ Load conversation context
    ├─ Invoke Agent (OpenAI SDK)
    │   ├─ Agent processes intent
    │   ├─ Agent invokes MCP tools
    │   └─ Agent generates response
    ├─ Persist message + tool invocations
    └─ Return response
PostgreSQL
    ├─ Conversations
    ├─ Messages
    ├─ Todos
    └─ ToolInvocations
```

## Local Setup (Post-Implementation)

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Docker (optional, for containerized setup)

### Installation

1. **Clone repository and switch to feature branch**:
   ```bash
   git clone <repo>
   cd <repo>
   git checkout 001-ai-todo-chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings:
   # DATABASE_URL=postgresql://user:pass@localhost/todo_chatbot
   # OPENAI_API_KEY=sk-...
   # JWT_SECRET=your-secret-key
   ```

4. **Initialize database**:
   ```bash
   # Run migrations
   alembic upgrade head
   ```

5. **Start MCP server** (in separate terminal):
   ```bash
   python -m src.mcp_server
   ```

6. **Start FastAPI app**:
   ```bash
   uvicorn src.api.main:app --reload
   ```

7. **Test the API**:
   ```bash
   curl -X POST http://localhost:8000/chat/messages \
     -H "Authorization: Bearer <jwt_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "conversation_id": null,
       "message": "Create a todo to buy groceries"
     }'
   ```

## Component Interactions

### Request Lifecycle

1. **Client sends request**: `POST /chat/messages` with user_id (JWT), conversation_id, message

2. **FastAPI validates**: Authorization, message format

3. **Load context**: Query PostgreSQL for conversation history (if conversation_id provided)

4. **Invoke agent**:
   ```python
   response = agent.process(
     context=prior_messages + current_message,
     tools=mcp_tools  # Available tools
   )
   ```

5. **Agent reasons**:
   - Reads: "Create a todo to buy groceries"
   - Infers: User wants to CREATE a todo
   - Invokes: create_todo(title="buy groceries", priority="medium")

6. **MCP Client routes tool call**:
   ```python
   result = mcp_client.invoke_tool(
     tool_name="create_todo",
     parameters={"title": "buy groceries", "priority": "medium"}
   )
   ```

7. **MCP Server executes**:
   ```python
   todo = todo_manager.create_todo(
     title="buy groceries",
     priority="medium",
     user_id=user_id
   )
   return {"success": true, "todo": todo, "error": null}
   ```

8. **Agent receives result** and generates response:
   ```
   "I've created a todo 'buy groceries' for you with medium priority."
   ```

9. **FastAPI persists** to PostgreSQL:
   - Message (role: assistant, content: "I've created...")
   - ToolInvocation (tool_name: create_todo, parameters, result)

10. **Client receives response** with current todos and tool audit trail

### Conversation Resumption

1. **Client sends request** with existing `conversation_id`

2. **FastAPI loads** all prior messages from database:
   ```sql
   SELECT * FROM messages
   WHERE conversation_id = ?
   ORDER BY timestamp ASC
   ```

3. **Agent receives** full context:
   ```
   [
     {role: "user", message: "Create a todo to buy groceries"},
     {role: "assistant", message: "I've created..."},
     {role: "user", message: "Show my todos"},
     {role: "assistant", message: "Here are your todos..."},
     {role: "user", message: "Mark groceries as done"}
   ]
   ```

4. **Agent maintains coherence** — knows prior context, user's intent is clear

5. **Tool is invoked** — `update_todo(id=todo-001, status=completed)`

6. **Response is generated** — "Done! I've marked 'buy groceries' as completed."

## File Structure

```
src/
├── api/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app, /chat/messages endpoint
│   └── routes/
│       └── chat.py                  # Chat route handler
├── services/
│   ├── __init__.py
│   ├── agent.py                     # OpenAI Agents SDK wrapper
│   ├── mcp_client.py                # MCP tool invocation
│   └── todo_manager.py              # Todo CRUD logic
├── models/
│   ├── __init__.py
│   ├── database.py                  # SQLModel schema (Conversation, Message, Todo, ToolInvocation)
│   └── schemas.py                   # Pydantic request/response
├── db/
│   ├── __init__.py
│   ├── connection.py                # PostgreSQL connection pool
│   └── migrations/                  # Alembic migrations
└── utils/
    ├── __init__.py
    ├── logging.py                   # Structured logging
    └── errors.py                    # Error handling

tests/
├── contract/
│   └── test_mcp_tools.py            # MCP tool contract validation
├── integration/
│   ├── test_chat_endpoint.py        # Full user journeys
│   └── test_conversation_persistence.py  # Session resumption
└── unit/
    ├── test_agent.py
    ├── test_todo_manager.py
    └── test_mcp_client.py

docker/
├── Dockerfile
└── docker-compose.yml
```

## Key Classes and Methods

### Agent Service (`src/services/agent.py`)

```python
class AgentService:
    def __init__(self, mcp_client: MCPClient):
        self.agent = openai.agents.Agent(...)
        self.mcp_client = mcp_client

    def process(self, context: List[Message], user_message: str) -> str:
        """
        Process user message and return agent response.
        - Formats context for agent
        - Invokes OpenAI Agents SDK
        - Routes tool calls to MCP client
        - Returns natural language response
        """
        ...
```

### MCP Client (`src/services/mcp_client.py`)

```python
class MCPClient:
    def invoke_tool(self, tool_name: str, parameters: dict) -> dict:
        """
        Invoke MCP tool.
        - Validates parameters
        - Calls MCP server
        - Returns result
        """
        ...
```

### Todo Manager (`src/services/todo_manager.py`)

```python
class TodoManager:
    def create_todo(self, title: str, description: str = None,
                    priority: str = "medium", user_id: str = None) -> Todo:
        """Create todo in database."""
        ...

    def read_todos(self, user_id: str, conversation_id: UUID = None) -> List[Todo]:
        """Retrieve todos for user."""
        ...

    def update_todo(self, todo_id: UUID, **kwargs) -> Todo:
        """Update todo fields."""
        ...

    def delete_todo(self, todo_id: UUID) -> bool:
        """Soft-delete todo (mark archived)."""
        ...
```

### FastAPI Chat Endpoint (`src/api/routes/chat.py`)

```python
@router.post("/messages")
async def chat_messages(request: ChatRequest, user_id: str = Depends(get_user_from_jwt)):
    """
    Stateless chat endpoint.
    - Load conversation context
    - Invoke agent
    - Persist message + tool invocations
    - Return response
    """
    ...
```

## Testing Strategy (Per Constitution: Test-First)

### Unit Tests
- `test_agent.py`: Agent processing, intent detection
- `test_todo_manager.py`: CRUD operations, validation
- `test_mcp_client.py`: Tool invocation, error handling

### Contract Tests
- `test_mcp_tools.py`: Tool signatures, parameter validation, response format

### Integration Tests
- `test_chat_endpoint.py`: Full user journeys (create, read, update, delete)
- `test_conversation_persistence.py`: Resume conversation, context loading

### Example Test (BDD format):

```python
def test_create_todo_via_chat():
    """US1: Create todo via natural language"""
    # Given: User sends create message
    request = ChatRequest(
        conversation_id=None,
        message="Create a todo to buy groceries"
    )

    # When: Agent processes request
    response = client.post("/chat/messages", json=request.dict())

    # Then: Todo is created and agent responds
    assert response.status_code == 200
    assert "created" in response.json()["response"].lower()
    assert len(response.json()["todos"]) == 1
    assert response.json()["todos"][0]["title"] == "buy groceries"
```

## Database Setup

### Schema Initialization

```bash
# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### Tables Created

- `conversations`: Conversation metadata
- `messages`: Chat messages (user + agent)
- `todos`: User todos
- `tool_invocations`: Audit log of tool calls

## Environment Variables

```
# Database
DATABASE_URL=postgresql://user:password@localhost/todo_chatbot
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Authentication
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO

# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001
```

## Debugging and Logging

### Structured Logging

All requests are logged with request ID for traceability:

```python
logger.info("Chat request", request_id=req_id, user_id=user_id, message=msg)
logger.info("Agent invoked tool", request_id=req_id, tool_name="create_todo", params=...)
logger.info("Tool result", request_id=req_id, tool_name="create_todo", result=...)
```

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG uvicorn src.api.main:app --reload
```

### Inspection Queries

Inspect tool invocations:

```sql
SELECT * FROM tool_invocations
WHERE message_id = 'msg-id'
ORDER BY timestamp ASC;
```

Inspect conversation history:

```sql
SELECT * FROM messages
WHERE conversation_id = 'conv-id'
ORDER BY timestamp ASC;
```

## Common Issues and Troubleshooting

### Issue: "Tool not found"
- **Cause**: MCP server not running or tool not registered
- **Fix**: Start MCP server (`python -m src.mcp_server`) before FastAPI

### Issue: "Conversation not found" (404)
- **Cause**: User attempting to access conversation they don't own
- **Fix**: Verify conversation_id matches user's conversations

### Issue: "Database connection failed"
- **Cause**: PostgreSQL not running or DATABASE_URL incorrect
- **Fix**: Check `.env`, verify `psql -U user -d todo_chatbot` works

### Issue: Slow responses (>3 seconds)
- **Cause**: Database query slow, MCP server slow, or agent slow
- **Fix**: Check database indexes, profile MCP tool latency, monitor agent API calls

## Performance Optimization Tips

1. **Database Indexes**: Ensure indexes on `(user_id, status)` and `(conversation_id, timestamp)`
2. **Connection Pool**: Tune `DATABASE_POOL_SIZE` based on concurrent users
3. **Agent Caching**: Cache conversation context in request scope (not global)
4. **MCP Tool Caching**: Avoid redundant tool calls (agent should learn from prior results)
5. **Conversation Retrieval**: Load only recent messages (e.g., last 50) for very long conversations (post-MVP optimization)

## References

- **Specification**: `./spec.md`
- **Implementation Plan**: `./plan.md`
- **Data Model**: `./data-model.md`
- **API Schema**: `./contracts/api-schema.md`
- **MCP Tools**: `./contracts/mcp-tools.md`
- **Constitution**: `../../.specify/memory/constitution.md`

---

**Next Step**: After design approval, run `/sp.tasks` to generate testable implementation tasks.
