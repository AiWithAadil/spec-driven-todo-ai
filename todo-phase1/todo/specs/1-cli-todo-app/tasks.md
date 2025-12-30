# Tasks: Python CLI Todo Application

**Input**: Design documents from `specs/1-cli-todo-app/`
**Prerequisites**: plan.md (✅), spec.md (✅), data-model.md (✅), contracts/cli-commands.md (✅), research.md (✅)

**Organization**: Tasks are grouped by user story (5 stories) to enable independent implementation and testing of each story.

**User Stories** (from spec.md):
- **US1 (P1)**: Add Task - Create tasks with descriptions
- **US2 (P1)**: View Tasks - Display all tasks with status
- **US3 (P2)**: Mark Task Complete - Toggle completion status
- **US4 (P2)**: Update Task - Modify task descriptions
- **US5 (P3)**: Delete Task - Remove tasks permanently

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

**Checkpoint**: After Phase 1, project structure is ready for foundational work

- [ ] T001 Create project structure per implementation plan (src/, tests/, docs/)
- [ ] T002 Initialize Python 3.8+ project with README.md and requirements.txt
- [ ] T003 [P] Configure pytest configuration (pytest.ini) and test discovery
- [ ] T004 [P] Create empty modules: src/todo_app.py, src/models.py, src/storage.py, src/commands.py, src/formatter.py, src/errors.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Checkpoint**: Foundation ready - all user stories can now proceed in parallel

### Error Handling Framework

- [ ] T005 Create custom exception classes in src/errors.py (TaskNotFoundError, InvalidTaskError, StorageError, CommandError)

### Data Model (Task Entity)

- [ ] T006 [P] Implement Task model in src/models.py with attributes: id, description, completed, created_at, updated_at
- [ ] T007 [P] Add Task validation methods: validate_description() and validate_id() with error messages
- [ ] T008 [P] Implement TaskList model in src/models.py with attributes: version, next_id, tasks[]
- [ ] T009 [P] Add TaskList methods: add_task(description), find_task(id), get_all_tasks()

### Storage Layer

- [ ] T010 Implement storage.py with file path resolution (cross-platform: ~/.todo/tasks.json on Unix, %USERPROFILE%\.todo\tasks.json on Windows)
- [ ] T011 Implement storage.load_tasks() to read JSON and deserialize into TaskList
- [ ] T012 Implement storage.save_tasks(task_list) to serialize and write JSON with atomic writes
- [ ] T013 Add storage.init_if_needed() to create directory and initialize empty task list on first run
- [ ] T014 [P] Add error handling in storage layer: catch IOError, JSON decode errors, permission errors

### Formatter (Output Display)

- [ ] T015 Implement formatter.py with format_task_list(tasks) returning formatted string for display
- [ ] T016 Implement formatter.format_confirmation(message) for success messages with ✓ prefix
- [ ] T017 Implement formatter.format_error(message) for error messages to stderr
- [ ] T018 [P] Add formatter helper: format_task_row(task) to display single task with ID, description, and status indicator

### CLI Foundation

- [ ] T019 Implement argparse setup in src/todo_app.py with main() entry point
- [ ] T020 Add subcommand definition for all 5 commands: add, list, view, complete, update, delete, help

---

## Phase 3: User Story 1 - Add Task (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks with descriptions; tasks are stored with unique IDs and displayed with confirmations

**Independent Test**: `todo add "Buy milk"` creates task with ID, `todo list` shows the new task, `todo add ""` displays error

### Implementation for User Story 1

- [ ] T021 [P] [US1] Implement add_task() command handler in src/commands.py (extract description argument, call models.TaskList.add_task())
- [ ] T022 [P] [US1] Add description validation in add_task: empty string check, length validation (1-1000 chars)
- [ ] T023 [US1] Integrate add_task with storage: load tasks, add task, save tasks to JSON (T021 + T011 + T012)
- [ ] T024 [US1] Add confirmation message output: "✓ Task added (ID: X)" via formatter.format_confirmation()
- [ ] T025 [US1] Add error handling for add_task: catch InvalidTaskError and display via formatter.format_error()
- [ ] T026 [US1] Wire add command to CLI dispatcher in main() argparse handler (src/todo_app.py)
- [ ] T027 [US1] Add unit tests for add_task validation in tests/test_commands.py (empty, whitespace, valid, max length)
- [ ] T028 [US1] Add integration test in tests/test_integration.py: add task → list tasks → verify new task appears

**Checkpoint**: User Story 1 complete. `todo add` fully functional. Can test independently: `python -m pytest tests/ -k US1`

---

## Phase 4: User Story 2 - View Tasks (Priority: P1)

**Goal**: Users can view all tasks in a clear, formatted list showing ID, description, and completion status

**Independent Test**: `todo list` displays all tasks with checkboxes, empty list shows "No tasks found"

### Implementation for User Story 2

- [ ] T029 [P] [US2] Implement list_tasks() command handler in src/commands.py (load all tasks, format output)
- [ ] T030 [P] [US2] Implement view_tasks() as alias for list_tasks() (both commands map to same handler)
- [ ] T031 [US2] Integrate with storage: load tasks from JSON via storage.load_tasks()
- [ ] T032 [US2] Implement task formatting in formatter.format_task_list(): display ID, description, status ([✓] or [ ])
- [ ] T033 [US2] Add empty list handling: display "No tasks found" when no tasks exist
- [ ] T034 [US2] Display task count summary: "(X tasks, Y complete)" at end of list
- [ ] T035 [US2] Wire list and view commands to CLI dispatcher in main() (src/todo_app.py)
- [ ] T036 [US2] Add unit tests in tests/test_commands.py: list with tasks, list with empty list, list with mixed status
- [ ] T037 [US2] Add integration test in tests/test_integration.py: add multiple tasks → list → verify all appear with correct status

**Checkpoint**: User Story 2 complete. `todo list` and `todo view` fully functional. Can test independently: `python -m pytest tests/ -k US2`

---

## Phase 5: User Story 3 - Mark Task Complete (Priority: P2)

**Goal**: Users can mark tasks as complete; completion status persists and is displayed in list view

**Independent Test**: `todo complete 1` marks task complete, `todo list` shows [✓] for completed task, completing already-complete task succeeds

### Implementation for User Story 3

- [ ] T038 [P] [US3] Implement complete_task(task_id) command handler in src/commands.py
- [ ] T039 [P] [US3] Add task ID validation in complete_task: numeric check, existence check (raises TaskNotFoundError if not found)
- [ ] T040 [US3] Integrate with storage: load tasks, find task by ID, set completed=true, update updated_at timestamp, save
- [ ] T041 [US3] Implement task lookup in models.TaskList.find_task(id) to support all ID operations
- [ ] T042 [US3] Add confirmation message: "✓ Task X marked as complete" via formatter.format_confirmation()
- [ ] T043 [US3] Add error handling: catch TaskNotFoundError, CommandError (non-numeric ID) and display errors
- [ ] T044 [US3] Wire complete command to CLI dispatcher in main() (src/todo_app.py)
- [ ] T045 [US3] Add idempotency test: mark already-complete task should succeed without error
- [ ] T046 [US3] Add unit tests in tests/test_commands.py: valid ID, non-existent ID, non-numeric ID, already complete
- [ ] T047 [US3] Add integration test in tests/test_integration.py: add task → complete → list → verify status changes and persists

**Checkpoint**: User Story 3 complete. `todo complete` fully functional. Can test independently: `python -m pytest tests/ -k US3`

---

## Phase 6: User Story 4 - Update Task (Priority: P2)

**Goal**: Users can modify task descriptions; changes persist and are displayed immediately

**Independent Test**: `todo update 1 "New desc"` updates description, `todo list` shows new description, error on non-existent task

### Implementation for User Story 4

- [ ] T048 [P] [US4] Implement update_task(task_id, new_description) command handler in src/commands.py
- [ ] T049 [P] [US4] Add task ID validation in update_task: numeric check, existence check (raises TaskNotFoundError)
- [ ] T050 [P] [US4] Add description validation in update_task: empty check, length validation (1-1000 chars)
- [ ] T051 [US4] Integrate with storage: load tasks, find task by ID, update description, update updated_at, save
- [ ] T052 [US4] Implement models.Task.update_description(new_desc) method for atomic update
- [ ] T053 [US4] Add confirmation message: "✓ Task X updated" via formatter.format_confirmation()
- [ ] T054 [US4] Add error handling: TaskNotFoundError, InvalidTaskError, CommandError with user-friendly messages
- [ ] T055 [US4] Wire update command to CLI dispatcher in main() (src/todo_app.py)
- [ ] T056 [US4] Add unit tests in tests/test_commands.py: valid update, non-existent ID, empty description, long description
- [ ] T057 [US4] Add integration test in tests/test_integration.py: add task → update → list → verify description changes

**Checkpoint**: User Story 4 complete. `todo update` fully functional. Can test independently: `python -m pytest tests/ -k US4`

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Users can permanently remove tasks; deletion persists across restarts and IDs are never reused

**Independent Test**: `todo delete 1` removes task, `todo list` no longer shows it, task ID never reappears

### Implementation for User Story 5

- [ ] T058 [P] [US5] Implement delete_task(task_id) command handler in src/commands.py
- [ ] T059 [P] [US5] Add task ID validation in delete_task: numeric check, existence check (raises TaskNotFoundError)
- [ ] T060 [US5] Integrate with storage: load tasks, find task by ID, remove from list, DO NOT change next_id, save
- [ ] T061 [US5] Implement models.TaskList.remove_task(id) method that removes task but preserves next_id
- [ ] T062 [US5] Add confirmation message: "✓ Task X deleted" via formatter.format_confirmation()
- [ ] T063 [US5] Add error handling: TaskNotFoundError, CommandError with user-friendly messages
- [ ] T064 [US5] Wire delete command to CLI dispatcher in main() (src/todo_app.py)
- [ ] T065 [US5] Add unit tests in tests/test_commands.py: valid delete, non-existent ID, non-numeric ID, verify ID reuse prevented
- [ ] T066 [US5] Add integration test in tests/test_integration.py: add → delete → add → verify new task gets next ID (not reused)

**Checkpoint**: User Story 5 complete. `todo delete` fully functional. All 5 core commands now working. Can test independently: `python -m pytest tests/ -k US5`

---

## Phase 8: Cross-Cutting Concerns & Polish

**Purpose**: Quality improvements, documentation, and final validation

**Checkpoint**: Application is production-ready

### Help System

- [ ] T067 Implement help_command() in src/commands.py showing all commands with examples
- [ ] T068 Wire help command to CLI dispatcher (supports `todo help`, `todo help <command>`)
- [ ] T069 Add -h/--help support to argparse for each subcommand

### Persistence & Edge Cases

- [ ] T070 Test data durability: add task → kill process → restart → verify task persists
- [ ] T071 Test rapid successive commands: execute 10+ commands in quick succession, verify no data loss
- [ ] T072 Test special characters in descriptions: quotes, unicode, newlines → verify handled correctly
- [ ] T073 Test max task list size: add 1000+ tasks → verify performance <1 second
- [ ] T074 Test file permission errors: simulate write-protected storage → verify error message

### Documentation & Examples

- [ ] T075 Update README.md with installation, usage examples, and troubleshooting
- [ ] T076 Verify quickstart.md examples work end-to-end with actual implementation
- [ ] T077 Add docstrings to all public functions in src/
- [ ] T078 Create development guide: how to extend with new commands

### Final Testing

- [ ] T079 Run full integration test suite: `pytest tests/test_integration.py -v`
- [ ] T080 [P] Run all unit tests: `pytest tests/test_commands.py tests/test_models.py tests/test_storage.py -v`
- [ ] T081 Run linting check on all src/ files for code quality
- [ ] T082 Verify command-line help and error messages are user-friendly
- [ ] T083 Test on all platforms (if possible): Linux, macOS, Windows

### Validation Against Specification

- [ ] T084 Verify all acceptance scenarios from User Stories 1-5 pass
- [ ] T085 Verify all functional requirements (FR-001 through FR-010) are satisfied
- [ ] T086 Verify success criteria (SC-001 through SC-006) are met
- [ ] T087 Verify all edge cases handled gracefully

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion ✅ BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 & US2 (P1): Can proceed in parallel (independent, both critical)
  - US3 & US4 (P2): Can proceed in parallel (both depend on US1+US2, but independent of each other)
  - US5 (P3): Can proceed in parallel after Foundational
  - Or sequential: US1 → US2 → US3 → US4 → US5 (safest MVP path)
- **Polish (Phase 8)**: Depends on all user stories being complete

### Task Dependencies Within Phases

**Phase 2 (Foundational)**:
- Error handling (T005) has no dependencies
- Data Model (T006-T009) can run in parallel; all 4 should complete before Storage
- Storage (T010-T014) depends on Data Model tasks
- Formatter (T015-T018) can run in parallel with Data Model & Storage
- CLI Foundation (T019-T020) depends on all above

**Phase 3 (US1 - Add)**:
- T021-T023 can run in parallel
- T024-T026 depend on T021-T023
- Tests (T027-T028) depend on command implementation

**Phases 4-7 (US2-US5)**:
- Within each story: Model tasks can run in parallel, then implementation, then tests
- Between stories: Each story independent; can overlap

### Parallel Opportunities

**Within Setup (Phase 1)**:
```
T003 (pytest config) and T004 (empty modules) can run in parallel
```

**Within Foundational (Phase 2)**:
```
T006, T007, T008, T009 (Data Model) - run in parallel
T015, T016, T017, T018 (Formatter) - run in parallel with Model tasks
```

**Across User Stories**:
```
After Foundational complete, these can run in parallel:
- Developer A: Phase 3 (US1 - Add)
- Developer B: Phase 4 (US2 - View)
- Developer C: Phase 5 (US3 - Complete)
- Developer D: Phase 6 (US4 - Update)
- Developer E: Phase 7 (US5 - Delete)
```

---

## Parallel Example: User Story 1 (Add Task)

```bash
# After Foundational tasks (T005-T020) are complete:

# These can run in parallel:
- T021: Implement add_task() command handler
- T022: Add description validation
- T027: Add unit tests for add_task

# Wait for T021 and T022 to complete, then:
- T023: Integrate with storage (depends on T021 + T022 + T011 + T012)
- T024: Add confirmation message (depends on T021)
- T028: Add integration test (depends on T026)

# Sequential within story:
T023 → T024 → T025 → T026 → T027 → T028
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

The absolute minimum to have a working application:

1. **Complete Phase 1**: Setup (T001-T004) ✅
2. **Complete Phase 2**: Foundational (T005-T020) ✅ CRITICAL
3. **Complete Phase 3**: User Story 1 - Add Task (T021-T028) ✅
4. **Complete Phase 4**: User Story 2 - View Tasks (T029-T037) ✅
5. **STOP and VALIDATE**: Test both stories independently
   - `todo add "Test"` → displays confirmation with ID
   - `todo list` → displays the new task with [ ] status
   - `python -m pytest tests/test_integration.py -v` → all pass
6. **Deploy/Demo**: Application is now usable (create and view tasks)

**Time estimate**: ~4-6 hours for experienced developer

### Incremental Delivery (All 5 Stories)

Each step adds value without breaking previous functionality:

1. Complete MVP (US1 + US2) → Deploy (create & view tasks)
2. Add US3 (Mark Complete) → Deploy (track progress)
3. Add US4 (Update) → Deploy (refine tasks)
4. Add US5 (Delete) → Deploy (cleanup tasks)
5. Add Phase 8 (Polish) → Deploy (final quality)

**Key**: At each checkpoint, the application remains fully functional

### Parallel Team Strategy

With 5 developers:

1. **Team meets**: Complete Phase 1 (Setup) together (30 mins)
2. **Team pair**: Complete Phase 2 (Foundational) together (2-3 hours)
3. **Team splits**:
   - Developer 1: Phase 3 (US1 - Add)
   - Developer 2: Phase 4 (US2 - View)
   - Developer 3: Phase 5 (US3 - Complete)
   - Developer 4: Phase 6 (US4 - Update)
   - Developer 5: Phase 7 (US5 - Delete)
4. **Team integrates**: Run full test suite, polish (Phase 8)

---

## Testing Strategy

### Unit Tests (Phase 2+)

Each task should have corresponding unit tests:
- Models: Test validation, state transitions (tests/test_models.py)
- Storage: Test load/save, error handling (tests/test_storage.py)
- Commands: Test each command with valid/invalid inputs (tests/test_commands.py)

### Integration Tests (Phase 3+)

End-to-end tests for each user story:
- Add task end-to-end
- View tasks end-to-end
- Each story independently, then combined

### Acceptance Tests

Verify acceptance scenarios from spec.md:
- 15 acceptance scenarios total (3 per user story)
- All must pass before story is considered complete

---

## Success Criteria (from spec.md)

These tasks must satisfy ALL success criteria:

- **SC-001**: ✅ All five core features implemented (add, view, complete, update, delete)
- **SC-002**: ✅ App handles valid/invalid input without crashing (error handling throughout)
- **SC-003**: ✅ Data persists across restarts (storage layer + JSON)
- **SC-004**: ✅ Error messages are clear and actionable (formatter layer)
- **SC-005**: ✅ View displays all tasks consistently with status (formatter + storage)
- **SC-006**: ✅ Commands complete <1 second (in-memory + simple JSON I/O)

---

## Notes

- **[P]**: Tasks marked [P] can run in parallel (different files, no dependencies)
- **[Story]**: Tasks labeled [US1-US5] map to specific user stories for traceability
- **Dependency arrows**: `→` means "depends on"
- **Test-first**: Write tests before implementation for maximum confidence
- **Commit frequently**: After each task or logical group
- **Stop at checkpoints**: Validate story independently at each checkpoint
- **Avoid**: Cross-story dependencies, vague tasks, same file conflicts

---

## Task Checklist for Implementation

Use this checklist to track progress:

```
Phase 1: Setup
  - [ ] T001-T004 complete

Phase 2: Foundational
  - [ ] T005 Error handling
  - [ ] T006-T009 Data models
  - [ ] T010-T014 Storage
  - [ ] T015-T018 Formatter
  - [ ] T019-T020 CLI foundation

Phase 3: US1 (Add Task)
  - [ ] T021-T026 Implementation
  - [ ] T027-T028 Testing
  - [ ] ✅ CHECKPOINT: US1 complete

Phase 4: US2 (View Tasks)
  - [ ] T029-T035 Implementation
  - [ ] T036-T037 Testing
  - [ ] ✅ CHECKPOINT: US2 complete

Phase 5: US3 (Complete)
  - [ ] T038-T044 Implementation
  - [ ] T045-T047 Testing
  - [ ] ✅ CHECKPOINT: US3 complete

Phase 6: US4 (Update)
  - [ ] T048-T055 Implementation
  - [ ] T056-T057 Testing
  - [ ] ✅ CHECKPOINT: US4 complete

Phase 7: US5 (Delete)
  - [ ] T058-T064 Implementation
  - [ ] T065-T066 Testing
  - [ ] ✅ CHECKPOINT: US5 complete

Phase 8: Polish
  - [ ] T067-T087 All polish tasks
  - [ ] ✅ FINAL: Application ready for deployment
```

---

## Status

**Tasks generated**: 87 total
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 16 tasks
- Phase 3 (US1 - Add): 8 tasks
- Phase 4 (US2 - View): 9 tasks
- Phase 5 (US3 - Complete): 10 tasks
- Phase 6 (US4 - Update): 10 tasks
- Phase 7 (US5 - Delete): 9 tasks
- Phase 8 (Polish): 21 tasks

**Status**: ✅ **READY FOR IMPLEMENTATION**

All tasks are atomic, independently testable, and reference the specification. Each user story can be implemented and deployed independently while maintaining a working application at each checkpoint.
