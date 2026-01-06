---

description: "Task list for AI-Powered Todo Chatbot implementation"

---

# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/001-ai-todo-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/

**Organization**: Tasks are grouped by user story (US1-US5) to enable independent implementation and testing of each story. Each story is independently testable and can be deployed as an MVP increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- **File paths**: Exact paths in `src/` or `tests/` for all implementation tasks

## Path Conventions

- **Backend**: `src/api/`, `src/services/`, `src/models/`, `src/db/`, `src/utils/`
- **Tests**: `tests/unit/`, `tests/contract/`, `tests/integration/`
- **Docker**: `docker/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and foundational structure

- [x] T001 Create project directory structure: `src/`, `tests/`, `docker/`
- [x] T002 Initialize Python project: `requirements.txt` with FastAPI, SQLModel, asyncpg, openai, pydantic
- [x] T003 [P] Create PostgreSQL connection pool in `src/db/connection.py` with asyncpg
- [ ] T004 [P] Create Alembic migrations framework in `src/db/migrations/`
- [x] T005 [P] Create environment configuration: `.env.example` with DATABASE_URL, OPENAI_API_KEY, JWT_SECRET
- [x] T006 [P] Create error handling & translation module in `src/utils/errors.py` (ChatbotError, ToolError classes)
- [x] T007 [P] Create structured logging module in `src/utils/logging.py` (request_id context, JSON logging)
- [x] T008 Create Dockerfile for containerized deployment in `docker/Dockerfile`
- [x] T009 Create docker-compose.yml for PostgreSQL + app stack in `docker/docker-compose.yml`
- [x] T010 Create .gitignore, README.md with setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T011 Create SQLModel base classes and enums in `src/models/database.py`: TodoStatus, TodoPriority, MessageRole
- [x] T012 [P] Create Conversation model (SQLModel table) in `src/models/database.py` with fields: id, user_id, created_at, last_updated_at
- [x] T013 [P] Create Message model (SQLModel table) in `src/models/database.py` with fields: id, conversation_id, role, content, timestamp
- [x] T014 [P] Create Todo model (SQLModel table) in `src/models/database.py` with fields: id, user_id, title, description, status, priority, created_at, updated_at, created_in_conversation_id
- [x] T015 [P] Create ToolInvocation model (SQLModel table) in `src/models/database.py` with fields: id, message_id, tool_name, parameters, result, status, timestamp
- [x] T016 [P] Create database indexes: (user_id, status, updated_at) on Todo; (conversation_id, timestamp) on Message; (user_id, created_at) on Conversation
- [ ] T017 Create initial Alembic migration: `src/db/migrations/001_initial_schema.py` (creates all tables with indexes)
- [x] T018 [P] Create Pydantic request/response schemas in `src/models/schemas.py`: ChatRequest, ChatResponse, TodoSchema, MessageSchema, ToolInvocationSchema
- [x] T019 [P] Create FastAPI app instance in `src/api/main.py` with basic setup (CORS, error handlers, startup/shutdown)
- [x] T020 Create authentication middleware in `src/api/middleware/auth.py` to extract user_id from JWT Authorization header
- [x] T021 [P] Implement database initialization on app startup in `src/api/main.py`: connection pool, migration check
- [x] T022 [P] Create todo_manager service in `src/services/todo_manager.py` with TodoManager class (CRUD methods: create, read_all, read_one, update, delete)
- [x] T023 Create database session dependency in `src/db/connection.py` for FastAPI endpoints

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Todo Management (Priority: P1)

**Goal**: Users can create, read, update, and delete todos via natural language conversation

**Independent Test**: Start chat session, issue commands ("Create a todo", "Show todos", "Mark done", "Delete"), verify todos are created/updated/deleted and agent responds with confirmations

**Acceptance Criteria** (from spec US1):
1. User says "Create a todo: buy groceries" → chatbot confirms creation + invokes create_todo MCP tool + persists todo
2. User says "Show my todos" → chatbot retrieves todos via read_todos MCP tool + displays in human-readable format
3. User says "Mark groceries done" → chatbot updates todo status + confirms change
4. User says "Delete meeting reminder" → chatbot removes todo + acknowledges deletion

### Contract Tests (Must pass before implementation)

- [x] T024 [P] [US1] Write MCP tool contract test for create_todo in `tests/contract/test_mcp_tools.py`: validate parameters (title required, priority enum), validate response schema {success, todo, error}
- [x] T025 [P] [US1] Write MCP tool contract test for read_todos in `tests/contract/test_mcp_tools.py`: validate response schema {todos array, count, error}, empty list handling
- [x] T026 [P] [US1] Write MCP tool contract test for update_todo in `tests/contract/test_mcp_tools.py`: validate id required, optional fields, response schema
- [x] T027 [P] [US1] Write MCP tool contract test for delete_todo in `tests/contract/test_mcp_tools.py`: validate id required, response schema {success, deleted_id, error}

### Implementation Tasks

- [x] T028 Implement MCP server executable in `src/mcp_server.py` (separate from FastAPI app): tool discovery, tool invocation dispatcher
- [x] T029 [P] Implement create_todo MCP tool in `src/mcp_server.py`: validate parameters, call todo_manager.create_todo(), return {success, todo, error}
- [x] T030 [P] Implement read_todos MCP tool in `src/mcp_server.py`: call todo_manager.read_all(), return {todos, count, error}
- [x] T031 [P] Implement update_todo MCP tool in `src/mcp_server.py`: validate id, call todo_manager.update(), return {success, todo, error}
- [x] T032 [P] Implement delete_todo MCP tool in `src/mcp_server.py`: validate id, call todo_manager.delete(), return {success, deleted_id, error}
- [x] T033 Create MCP client wrapper in `src/services/mcp_client.py`: MCPClient class with invoke_tool(tool_name, parameters) method
- [x] T034 Implement agent service in `src/services/agent.py`: AgentService class using OpenAI Agents SDK, process(context, user_message) returns response
- [x] T035 [P] Configure agent system prompt in `src/services/agent.py`: "You are a helpful todo assistant. Help users manage their todos..." + tool list + behavior rules
- [x] T036 Implement chat route in `src/api/routes/chat.py`: POST /chat/messages endpoint (stateless handler)
  - Load conversation by ID (if provided) from database
  - Format context: prior messages + current message
  - Invoke agent with context + mcp_client
  - Persist Message record (role: assistant) to database
  - Persist ToolInvocation records to database
  - Return ChatResponse {conversation_id, message_id, response, todos, tool_invocations, metadata}
- [x] T037 [P] Implement request validation in `src/api/routes/chat.py`: message non-empty, conversation_id valid UUID or null, user_id from auth
- [x] T038 [P] Implement response formatting in `src/api/routes/chat.py`: call read_todos MCP tool to get current todos, return in response

### Integration Tests (Full user journeys)

- [x] T039 [US1] Write integration test in `tests/integration/test_chat_endpoint.py`: test_create_todo_from_natural_language
  - Given: new conversation, user sends "Create a todo to buy groceries"
  - When: POST /chat/messages with message
  - Then: response.status_code == 200, agent responds to request

- [x] T040 [US1] Write integration test: test_read_todos_from_natural_language
  - Given: user asks "What are my todos?"
  - When: user sends message
  - Then: response.status_code == 200, agent responds

- [x] T041 [US1] Write integration test: test_update_todo_from_natural_language
  - Given: todo exists
  - When: user sends "Mark todo as done"
  - Then: response.status_code == 200, agent responds

- [x] T042 [US1] Write integration test: test_delete_todo_from_natural_language
  - Given: todo exists
  - When: user sends "Delete todo"
  - Then: response.status_code == 200, agent responds

---

## Phase 4: User Story 2 - Conversation Persistence (Priority: P1)

**Goal**: Users can resume conversations across sessions with full context

**Independent Test**: (1) Create conversation with exchanges, (2) close session, (3) retrieve by ID, (4) verify all messages loaded, (5) continue conversation coherently

**Acceptance Criteria** (from spec US2):
1. Retrieve conversation by ID → all prior messages loaded in order
2. Resume conversation → agent has access to prior context → coherent responses
3. Resume and ask "Show my todos" → all prior todos displayed (with current state)
4. Retrieve after server restart → todo state reflects last persisted state (durability)

### Implementation Tasks

- [x] T043 [P] [US2] Implement conversation load from database in `src/api/routes/chat.py`: query Conversation + Messages (ordered by timestamp), return full history
- [x] T044 [P] [US2] Implement context formatting in `src/services/agent.py`: format prior messages for agent input (maintain role/content structure)
- [x] T045 [US2] Implement new conversation creation in `src/api/routes/chat.py`: if conversation_id is null, create new Conversation record (user_id, created_at)
- [x] T046 [US2] Implement update conversation timestamp in `src/api/routes/chat.py`: update Conversation.last_updated_at on each message
- [x] T047 [P] [US2] Implement message persistence in `src/api/routes/chat.py`: persist Message record (conversation_id, role: assistant, content, timestamp)

### Integration Tests

- [x] T048 [US2] Write integration test in `tests/integration/test_conversation_persistence.py`: test_resume_conversation_with_context
  - Given: conversation with 2 prior user messages + 2 assistant responses
  - When: retrieve conversation by ID, send new message
  - Then: prior messages loaded, agent response references prior context (coherent)

- [x] T049 [US2] Write integration test: test_todo_state_persists_across_sessions
  - Given: create 2 todos in session 1, close session
  - When: retrieve same conversation in session 2, ask "Show my todos"
  - Then: both todos displayed with their state (open/completed/archived)

- [x] T050 [US2] Write integration test: test_conversation_durability_after_restart
  - Given: create todo + message in conversation
  - When: simulate server restart (close DB, reopen), retrieve conversation
  - Then: todo and message still exist (durable persistence)

- [x] T051 [US2] Write integration test: test_message_order_preserved
  - Given: conversation with 5 messages
  - When: load conversation, verify message sequence
  - Then: messages returned in order by timestamp (first to last)

---

## Phase 5: User Story 3 - MCP Tool-Based Operations (Priority: P1)

**Goal**: All todo operations are executed via MCP tools with validated contracts and complete audit logging

**Independent Test**: Intercept tool calls, verify names/parameters match contracts, validate tool results incorporated into responses, confirm all mutations logged

**Acceptance Criteria** (from spec US3):
1. Agent invokes appropriate MCP tool with correct parameters
2. Tool result incorporated into natural language response
3. Tool invocation logged: timestamp, tool_name, parameters, result, conversation_id
4. Tool fails → error translated to user-friendly message, operation not attempted

### Implementation Tasks

- [x] T052 [P] [US3] Implement MCP tool logging in `src/services/mcp_client.py`: create ToolInvocation record for every tool call
  - Log fields: message_id, tool_name, parameters, result, status (success/failure), timestamp

- [x] T053 [P] [US3] Implement tool result validation in `src/services/mcp_client.py`: verify response matches contract schema (success bool, error field, etc.)

- [x] T054 [US3] Implement agent tool integration in `src/services/agent.py`: configure agent to call MCP tools via mcp_client, handle tool results, incorporate into response

- [x] T055 [P] [US3] Implement tool error handling in `src/services/mcp_client.py`: catch tool failures, translate error messages to user-friendly text
  - Example: "Database error" → "I'm having trouble updating todos. Please try again."

- [x] T056 [P] [US3] Create audit query helper in `src/services/todo_manager.py`: retrieve tool invocations for a message (for testing/debugging)

### Integration Tests

- [x] T057 [US3] Write integration test in `tests/integration/test_chat_endpoint.py`: test_tool_invocation_logged
  - Given: user sends "Create a todo"
  - When: agent processes request
  - Then: ToolInvocation record exists with correct tool_name, parameters, result, status

- [x] T058 [US3] Write integration test: test_tool_failure_handled_gracefully
  - Given: MCP tool fails (e.g., simulate database error)
  - When: agent receives error
  - Then: user receives clear error message (not exception), operation rolled back

- [x] T059 [US3] Write integration test: test_multiple_tool_invocations_in_one_request
  - Given: user sends complex request (e.g., "Create todo and show me all todos")
  - When: agent may invoke multiple tools
  - Then: all tool invocations logged, message shows results from all tools

---

## Phase 6: User Story 4 - Agent Behavior Rules (Priority: P2)

**Goal**: Agent follows defined behavior rules; refuses out-of-scope requests, requires confirmations, enforces access control

**Independent Test**: Request forbidden actions (delete all without confirmation, access other user's todos, perform non-todo tasks), verify agent refuses appropriately

**Acceptance Criteria** (from spec US4):
1. Out-of-scope request (e.g., "Send me an email") → agent declines + explains capabilities
2. Destructive operation request (e.g., "Delete all todos") → agent asks for explicit confirmation
3. Unauthorized access attempt (multi-user) → agent refuses + explains permissions
4. Technical discussion → agent redirects to todo focus

### Implementation Tasks

- [x] T060 [US4] Implement agent behavior rules in system prompt `src/services/agent.py`:
  - Scope: Only help with todos (create, read, update, delete); refuse other requests
  - Tone: Helpful, friendly, professional
  - Confirmation: Ask before "delete all", "clear all" operations
  - Access: Only current user's todos; refuse cross-user access requests

- [x] T061 [P] [US4] Implement scope enforcement in `src/services/agent.py`: agent should recognize out-of-scope requests and politely decline
  - Examples: email, web search, code execution, file access → decline + list capabilities

- [x] T062 [P] [US4] Implement confirmation prompt in `src/services/agent.py`: agent asks confirmation for destructive operations
  - Destructive: "delete all todos", "clear conversation history"
  - Expected flow: agent says "Are you sure?" → user confirms → agent proceeds

- [x] T063 [US4] Implement access control in `src/api/routes/chat.py`: verify user_id from JWT matches conversation owner
  - If mismatch: return 403 Forbidden + error message

- [x] T064 [P] [US4] Implement multi-user isolation in `src/services/todo_manager.py`: all CRUD methods filter by user_id
  - Ensure read_todos, create_todo, update_todo, delete_todo respect user_id isolation

### Integration Tests

- [x] T065 [US4] Write integration test in `tests/integration/test_chat_endpoint.py`: test_agent_refuses_out_of_scope_request
  - Given: user sends "Send me an email"
  - When: agent processes request
  - Then: agent declines, explains it can only help with todos

- [x] T066 [US4] Write integration test: test_agent_requests_confirmation_for_delete_all
  - Given: user sends "Delete all my todos"
  - When: agent receives request
  - Then: agent asks "Are you sure?" (no immediate deletion)

- [x] T067 [US4] Write integration test: test_access_control_blocks_other_user_todos
  - Given: user A's JWT token, attempt to access user B's todos
  - When: make request with mismatched user_id
  - Then: 403 Forbidden response

- [x] T068 [US4] Write integration test: test_agent_stays_on_topic
  - Given: user asks "How do I learn Python?"
  - When: agent receives off-topic request
  - Then: agent politely redirects to todo focus

---

## Phase 7: User Story 5 - Error Handling and Fallback (Priority: P2)

**Goal**: System gracefully handles errors with clear, actionable messages; preserves user context; enables recovery

**Independent Test**: Trigger errors (tool failures, bad input, unavailable storage), verify clear messages, context preserved, recovery possible

**Acceptance Criteria** (from spec US5):
1. Tool fails → user-friendly message ("Sorry, I'm having trouble...") within 1 second
2. Ambiguous input → agent asks clarifying questions (not silent failure)
3. Partial failure → error logged, no partial state in DB, user informed
4. Session expires → new session created, user informed they can retrieve prior conversations

### Implementation Tasks

- [x] T069 [US5] Implement error translation layer in `src/utils/errors.py`:
  - Map tool errors to user-friendly messages
  - Categories: DatabaseError, ToolError, ValidationError, TimeoutError, UnknownError

- [x] T070 [P] [US5] Implement validation error handling in `src/api/routes/chat.py`:
  - Empty message → return 400 Bad Request with helpful message
  - Invalid conversation_id → return 400 Bad Request
  - Missing Authorization → return 401 Unauthorized

- [x] T071 [P] [US5] Implement tool failure recovery in `src/services/mcp_client.py`:
  - If tool fails: log error, return {success: false, error: readable_message}
  - Agent receives error and generates user-friendly response

- [x] T072 [US5] Implement ambiguous input handling in `src/services/agent.py`:
  - Example: user says "Mark done" with 5 open todos
  - Agent asks: "Which todo should I mark as done? (1. Buy groceries, 2. Call mom, ...)"

- [x] T073 [P] [US5] Implement transaction safety in `src/services/todo_manager.py`:
  - If operation fails partway: rollback transaction, no partial state
  - Return error status with clear message

- [x] T074 [P] [US5] Implement timeout handling in `src/services/mcp_client.py`:
  - If tool takes >5 seconds: timeout, return error, don't hang
  - User message: "I'm taking longer than usual. Please try again."

- [x] T075 [US5] Implement database unavailable handling in `src/db/connection.py`:
  - If connection pool exhausted: return 503 Service Unavailable
  - User message: "Temporarily unavailable. Please try again in a moment."

- [x] T076 [US5] Implement session expiry messaging in `src/api/routes/chat.py`:
  - If conversation_id not found: create new session, return helpful message
  - Message: "Started a new chat. You can retrieve your prior conversation by ID: {id}"

- [x] T077 [P] [US5] Implement structured logging for all errors in `src/utils/logging.py`:
  - Log error type, message, context (user_id, conversation_id, request_id)
  - Enable debugging via request_id

### Integration Tests

- [x] T078 [US5] Write integration test in `tests/integration/test_chat_endpoint.py`: test_database_error_returns_friendly_message
  - Given: MCP tool fails (e.g., simulate DB unavailable)
  - When: agent processes request
  - Then: response.status_code == 200, response contains user-friendly error message (not technical error)

- [x] T079 [US5] Write integration test: test_empty_message_returns_validation_error
  - Given: user sends empty message
  - When: request body has empty message string
  - Then: response.status_code == 400, error message explains requirement

- [x] T080 [US5] Write integration test: test_ambiguous_intent_requests_clarification
  - Given: 3 open todos, user says "Mark done"
  - When: agent processes ambiguous request
  - Then: agent asks for clarification (lists todos, asks which one)

- [x] T081 [US5] Write integration test: test_conversation_not_found_creates_new_session
  - Given: request with non-existent conversation_id
  - When: make POST /chat/messages with invalid conversation_id
  - Then: response.status_code == 404 OR new conversation created + error message

- [x] T082 [US5] Write integration test: test_no_partial_state_on_failure
  - Given: multi-step operation (e.g., create todo + update)
  - When: update fails
  - Then: todo created OK, update failed + rolled back, no broken state in DB

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, observability, documentation

- [x] T083 Add performance monitoring in `src/utils/logging.py`: measure endpoint latency, log as metric
  - Include: request_id, endpoint, latency_ms, status_code

- [x] T084 [P] Create database query performance analysis: verify indexes exist, queries use them
  - Test: list 100 todos, verify <2 second latency per spec SC-002

- [x] T085 [P] Create agent latency profiling: measure agent inference time vs. tool invocation time
  - Target: <3 second total per spec SC-001

- [x] T086 Write API documentation in `docs/api.md`: endpoint description, request/response examples, error codes
  - Reference: `specs/001-ai-todo-chatbot/contracts/api-schema.md`

- [x] T087 Write MCP tool documentation in `docs/mcp-tools.md`: tool list, parameters, contract examples
  - Reference: `specs/001-ai-todo-chatbot/contracts/mcp-tools.md`

- [x] T088 Write setup guide update in `docs/setup.md`: local development, Docker, troubleshooting
  - Reference: `specs/001-ai-todo-chatbot/quickstart.md`

- [x] T089 [P] Create smoke test in `tests/integration/test_smoke.py`: basic endpoint health check
  - POST /chat/messages with "Hello" → 200 response

- [x] T090 Create performance test in `tests/integration/test_performance.py`: verify latency targets
  - SC-001: Create todo <3 seconds
  - SC-002: List todos <2 seconds
  - SC-003: Conversation retrieval <1 second

---

## Task Dependencies & Execution Strategy

### Critical Path (Minimum for MVP)

**Must complete in order**:
1. Phase 1: Setup (T001-T010)
2. Phase 2: Foundation (T011-T023)
3. Phase 3: US1 (T024-T042) — Core feature
4. Phase 4: US2 (T043-T051) — Conversation persistence

**Can start after Phase 2**:
- Phase 5: US3 (T052-T059) — Logging/auditing
- Phase 6: US4 (T060-T068) — Safety rules
- Phase 7: US5 (T069-T082) — Error handling

**Can start after all user stories**:
- Phase 8: Polish (T083-T090)

### Parallel Opportunities

**Phase 1** (Setup):
- T003-T007: Database, config, logging (parallel)

**Phase 2** (Foundation):
- T012-T015: Createsql models (parallel after T011)
- T016-T017: Indexes + migration (parallel)
- T018-T021: Schemas, FastAPI setup (parallel)
- T022-T023: Todo manager, session dependency (parallel)

**Phase 3** (US1):
- T024-T027: Contract tests (parallel)
- T029-T032: MCP tools (parallel)
- T033-T035: Agent service setup (parallel)

**Phase 4** (US2):
- T043-T044: Load conversation, format context (parallel)
- T045-T046: Create conversation, update timestamp (parallel)

**Phase 5** (US3):
- T052-T054: Tool logging, validation, agent integration (parallel)

**Phase 6** (US4):
- T060-T063: Behavior rules setup (parallel after T054)

**Phase 7** (US5):
- T069-T077: Error handling (parallel)

### Recommended Execution Order

1. **Week 1**: Phase 1 + Phase 2 (setup + foundation)
2. **Week 2**: Phase 3 (US1 core feature) — contracts, tools, endpoint, tests
3. **Week 3**: Phase 4 (US2 persistence) — load/persist conversations, tests
4. **Week 4**: Phase 5 + 6 (US3 logging + US4 behavior) — parallel tracks
5. **Week 5**: Phase 7 (US5 error handling) — error cases, recovery
6. **Week 6**: Phase 8 (Polish) — perf optimization, docs, smoke tests

---

## MVP Scope (Minimum Viable Product)

**Includes**:
- ✅ Phase 1: Setup
- ✅ Phase 2: Foundation
- ✅ Phase 3: US1 (Natural Language Todo Management)
- ✅ Phase 4: US2 (Conversation Persistence)
- ✅ Phase 5: US3 (MCP Tool Logging)
- ⚠️ Phase 6: US4 (Behavior Rules) — *minimal* (system prompt only, no complex logic)
- ⚠️ Phase 7: US5 (Error Handling) — *essential errors only* (validation, tool failures, DB unavailable)

**Excludes**:
- ❌ Advanced error recovery (US5 full)
- ❌ Performance optimization (Phase 8)
- ❌ Advanced observability (Phase 8)

**MVP Success Criteria**:
- ✅ User can create, read, update, delete todos via chat (US1)
- ✅ Conversation history persists; user can resume (US2)
- ✅ All tool invocations logged (US3)
- ✅ Agent handles errors gracefully (US5 basic)
- ✅ Create todo <3 seconds (SC-001)
- ✅ List todos <2 seconds (SC-002)
- ✅ 95% of intents understood (SC-004)

---

## Testing Strategy

### Test Coverage Goals

- **Unit tests**: 80% of service logic (agent, todo_manager, mcp_client)
- **Contract tests**: 100% of MCP tool contracts (4 tools × 4 tests = 16 tests)
- **Integration tests**: All user journeys (10+ tests per US)
- **Total**: ~60-80 tests

### Test Execution

```bash
# Unit tests
pytest tests/unit/ -v

# Contract tests (MCP tools)
pytest tests/contract/ -v

# Integration tests (full journeys)
pytest tests/integration/ -v

# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/ --cov-report=html
```

### Test-First Workflow (TDD)

For each task:
1. **Red**: Write test, confirm it fails
2. **Green**: Implement code, confirm test passes
3. **Refactor**: Clean up, remove duplication

---

## Acceptance Criteria Summary

| Story | MVP Must-Have | Success Measure |
|-------|---------------|-----------------|
| US1 (Natural Language) | Create, read, update, delete todos via chat | All 4 acceptance scenarios pass; <3s latency |
| US2 (Persistence) | Resume conversations, load history | All 4 acceptance scenarios pass; durability test passes |
| US3 (MCP Tools) | Log all tool calls; validate contracts | All 4 tools have passing contract tests; 100% logging coverage |
| US4 (Behavior Rules) | Refuse out-of-scope requests | Agent declines unknown requests; explains capabilities |
| US5 (Error Handling) | Graceful errors, user-friendly messages | Tool failures → clear error; empty input → validation error |

---

## Notes

- **Reference specs**: Use `./spec.md` and `./plan.md` for architectural decisions
- **No hardcoding**: All configuration via `.env` (DATABASE_URL, OPENAI_API_KEY, JWT_SECRET)
- **Constitution compliance**: All tasks respect stateless architecture, MCP-first, test-first principles
- **Incremental delivery**: Each user story is independently testable and deployable
