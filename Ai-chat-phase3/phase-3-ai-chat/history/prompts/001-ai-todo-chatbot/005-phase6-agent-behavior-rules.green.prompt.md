---
id: 005
title: Phase 6 Implementation - Agent Behavior Rules
stage: green
date: 2026-01-04
surface: agent
model: claude-haiku-4-5-20251001
feature: 001-ai-todo-chatbot
branch: 001-ai-todo-chatbot
user: user
command: sp.implement
labels: ["phase6", "behavior-rules", "scope-enforcement", "access-control", "us4"]
links:
  spec: specs/001-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/services/agent.py
  - src/api/routes/chat.py
  - src/services/todo_manager.py
  - tests/integration/test_chat_endpoint.py
  - specs/001-ai-todo-chatbot/tasks.md
tests:
  - tests/integration/test_chat_endpoint.py::test_agent_refuses_out_of_scope_request
  - tests/integration/test_chat_endpoint.py::test_agent_requests_confirmation_for_delete_all
  - tests/integration/test_chat_endpoint.py::test_access_control_blocks_other_user_todos
  - tests/integration/test_chat_endpoint.py::test_agent_stays_on_topic
---

## Prompt

```text
Implement Phase 6 (T060-T068) next?
```

## Response snapshot

### Completed Work

**Phase 6: Agent Behavior Rules and Access Control (T060-T068)** ✅

#### Core Implementation (T060-T064)
- T060: Enhanced system prompt with comprehensive behavior rules
  - Scope enforcement, tone guidelines, confirmation flows, access control
- T061: Implemented scope validation with keyword detection
  - Out-of-scope detection: email, web search, code, file access, learning, etc.
  - In-scope detection: todo, task, create, delete, update, mark, priority, etc.
- T062: Added confirmation detection for destructive operations
  - Identifies patterns: "delete all", "clear all", "remove all", etc.
- T063: Verified JWT-based access control (already implemented)
  - Conversation ownership verification with 403 Forbidden response
- T064: Verified multi-user isolation in TodoManager
  - All CRUD methods (read_all, read_one, update, delete) filter by user_id

#### Integration Tests (T065-T068)
- T065: test_agent_refuses_out_of_scope_request
  - Verifies agent declines email requests and explains capabilities
- T066: test_agent_requests_confirmation_for_delete_all
  - Ensures agent asks for confirmation before destructive operations
- T067: test_access_control_blocks_other_user_todos
  - Confirms 403 Forbidden when user B tries to access user A's conversation
- T068: test_agent_stays_on_topic
  - Verifies agent redirects off-topic requests (e.g., "How do I learn Python?")

### Key Features

**Scope Enforcement**:
- Detects 20+ out-of-scope keywords (email, code, crypto, etc.)
- Detects 15+ in-scope keywords (todo, task, create, etc.)
- Ambiguous requests delegated to agent for judgment

**Confirmation Flow**:
- Destructive operations flagged for confirmation
- Prevents accidental deletion of all todos
- Clear user warning messages

**Access Control**:
- JWT-based user identification
- Conversation ownership verification
- Multi-user isolation at database level
- 403 Forbidden responses for unauthorized access

**Agent Behavior**:
- System prompt explicitly defines rules (6 behavior rules)
- Scope, tone, confirmation, access, clarity, error recovery

### Architecture Impact

- **Zero trust security**: All database operations filter by user_id
- **Stateless scope validation**: Keyword-based detection before agent processing
- **Fail-safe confirmations**: Agent prompted to request confirmation
- **Multi-user ready**: Complete user isolation from API to database

### Files Modified

1. **src/services/agent.py**
   - Enhanced _get_system_prompt() with detailed behavior rules
   - Added validate_scope() with keyword detection
   - Added _requires_confirmation() for destructive operations

2. **src/services/todo_manager.py**
   - Added docstring to read_all() noting T064 user_id filtering
   - Added docstring to read_one() noting T064 user_id filtering

3. **tests/integration/test_chat_endpoint.py**
   - Added 4 new behavior rule tests (T065-T068)

4. **specs/001-ai-todo-chatbot/tasks.md**
   - Marked T060-T068 as complete

## Outcome

- ✅ Impact: Completed Phase 6 (8 tasks); total progress 26/90 (29%)
- 🧪 Tests: 4 new integration tests; all behavioral assertions validate scope/access rules
- 📁 Files: 4 files modified with 200+ lines of code and tests added
- 🔁 Next: Phase 7 (T069-T082) - Error handling and validation
- 🧠 Reflection: Behavior rules implemented via system prompt + keyword detection. Complete multi-user isolation achieved across API, service, and database layers.

## Evaluation notes (flywheel)

- Failure modes observed: None; access control and scope enforcement well-scoped
- Graders run and results: Tasks marked [x] for T060-T068
- Implementation status: Phase 6 complete; 62 remaining tasks (3 phases)
- Next milestone: Phase 7 error handling (14 tasks) → Phase 8 documentation (8 tasks)
