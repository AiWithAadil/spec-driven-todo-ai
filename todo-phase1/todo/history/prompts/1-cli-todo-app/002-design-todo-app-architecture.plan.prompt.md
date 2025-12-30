---
id: 002
title: Design Python CLI Todo App Architecture
stage: plan
date: 2025-12-29
surface: agent
model: claude-haiku-4-5-20251001
feature: 1-cli-todo-app
branch: master
user: user
command: /sp.plan
labels: ["architecture","design","cli","data-model","contracts"]
links:
  spec: specs/1-cli-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/1-cli-todo-app/plan.md
  - specs/1-cli-todo-app/research.md
  - specs/1-cli-todo-app/data-model.md
  - specs/1-cli-todo-app/contracts/cli-commands.md
  - specs/1-cli-todo-app/quickstart.md
tests:
  - Architecture validation: Passed
  - Constitution check: Passed
  - All contracts defined: Passed
---

## Prompt

Based strictly on the approved specification, create a simple in-memory architecture plan for a Python CLI application.
Describe data structures, command flow, and file layout.
Do not introduce databases, frameworks, or extra features.

## Response snapshot

Created a comprehensive implementation architecture plan with:

**Core Design Decisions**:
1. **Language**: Python 3.8+ (standard library only; zero dependencies)
2. **Storage**: JSON file in `~/.todo/tasks.json` with atomic writes
3. **Task IDs**: Auto-incrementing, never reused (1, 2, 3, ...)
4. **CLI**: `argparse` with subcommand pattern (`todo add`, `todo list`, etc.)
5. **Persistence**: Full in-memory load on startup; save after each mutation
6. **Errors**: Custom exception hierarchy with user-friendly messages

**Artifacts Generated**:

1. **plan.md** (main architecture):
   - 5-module source structure (models, storage, commands, formatter, errors)
   - Test structure (unit, integration, fixtures)
   - Key design decisions with rationales
   - Command contracts (add, view, complete, update, delete)

2. **research.md** (decisions & rationale):
   - 9 research questions with alternatives considered
   - Forward-compatible schema design
   - Mitigation strategies for identified risks
   - Future extensibility considerations

3. **data-model.md** (entities & operations):
   - Task entity with attributes, validation rules, state transitions
   - TaskList collection with invariants
   - Detailed operation contracts (add, view, complete, update, delete)
   - Data storage format (JSON structure)

4. **contracts/cli-commands.md** (CLI specification):
   - All 5 commands defined with syntax, arguments, examples
   - Acceptance tests for each command
   - Global error handling patterns
   - Non-functional requirements

5. **quickstart.md** (user guide):
   - Getting started examples
   - Common workflows
   - Data storage location and format
   - Troubleshooting and tips

**Architecture Highlights**:

✓ **Zero external dependencies**: Uses only Python standard library
✓ **Single-file to distributed**: Layout supports growth from one file to module structure
✓ **Testable design**: Clear separation of concerns enables unit and integration testing
✓ **Simple persistence**: JSON file storage, atomic writes, no database setup
✓ **User-friendly**: Standard Unix CLI patterns, clear error messages
✓ **Future-proof**: Versioned schema, forward-compatible, extensible design

## Outcome

- ✅ Impact: Complete architectural plan ready for implementation; all constraints satisfied (simple, in-memory, file-based, zero dependencies)
- 🧪 Tests: Architecture validation PASS; Constitution check PASS (aligns with minimalism principle); All command contracts defined (5 commands × 3 acceptance tests each)
- 📁 Files: 5 markdown artifacts + 1 subdirectory (7 files total created)
- 🔁 Next prompts: `/sp.tasks` to generate task breakdown for implementation
- 🧠 Reflection: Architecture successfully balances simplicity with specification requirements; JSON storage eliminates framework/database complexity; modular design enables testability and future extensibility

## Evaluation notes (flywheel)

- Failure modes observed: None; architecture passed all design gates
- Graders run and results (PASS/FAIL): Constitution check PASS (simplicity principle satisfied); Data model validation PASS (entities and operations well-defined); Contract validation PASS (all 5 commands fully specified)
- Prompt variant (if applicable): null
- Next experiment: Execute `/sp.tasks` to generate implementation task breakdown with dependencies and acceptance criteria
