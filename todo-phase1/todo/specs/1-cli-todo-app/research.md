# Research: Python CLI Todo Application

**Feature**: 1-cli-todo-app | **Date**: 2025-12-29

This document captures research decisions and architectural choices made during Phase 0 planning.

---

## Research Questions & Decisions

### 1. Language and Runtime

**Question**: What language version and runtime should be targeted?

**Decision**: Python 3.8+

**Rationale**:
- Python 3.8 is stable, widely available, and near end-of-life (December 2024), ensuring broad compatibility
- Support for Python 3.8+ future-proofs the application for security updates
- Python 3.8+ includes all necessary standard library features (`argparse`, `json`, `pathlib`, `datetime`)
- No external dependencies required; significantly reduces operational complexity
- Simple syntax makes code maintainable and testable

**Alternatives Considered**:
- **Go**: Fast, single binary, but verbose for CLI; overkill for this use case
- **Rust**: Powerful, but steep learning curve; unnecessary for single-user file-based app
- **Node.js/TypeScript**: Good option, but requires runtime installation; Python already common
- **Java**: Too heavyweight; Spring Boot or similar frameworks add unnecessary complexity

**Conclusion**: ✅ Python 3.8+ selected for simplicity, ubiquity, and speed of development

---

### 2. Storage Mechanism

**Question**: How should tasks be persisted across application restarts?

**Decision**: JSON file in user's home directory (`~/.todo/tasks.json` on Unix, `%USERPROFILE%\.todo\tasks.json` on Windows)

**Rationale**:
- Specification assumes simple file storage (see Assumptions section of spec.md)
- JSON is human-readable, facilitating debugging and manual inspection
- No database setup required; works on any machine with filesystem
- Python's `json` module handles serialization/deserialization without dependencies
- Sufficient for single-user, low-volume use case (sub-MB files for 1000+ tasks)
- Atomic writes using pathlib ensure data safety

**Alternatives Considered**:
- **SQLite**: Common recommendation for Python; adds ~500KB dependency; overcomplicated for this schema
- **In-memory only**: Violates FR-007 (data persistence requirement)
- **CSV**: Less structured; poor handling of special characters in descriptions
- **YAML**: More human-friendly than JSON, but requires external dependency (PyYAML)
- **XML**: Verbose, unnecessarily complex
- **Protocol Buffers/MessagePack**: Over-engineered for single-user app

**Conclusion**: ✅ JSON file-based storage selected for simplicity and zero dependencies

---

### 3. Task Identification Strategy

**Question**: How should tasks be uniquely identified and referenced?

**Decision**: Auto-incrementing numeric IDs (1, 2, 3, ...) stored in JSON metadata; IDs never reuse

**Rationale**:
- Specification explicitly assumes simple index/ID system (Assumptions: "Tasks are uniquely identified by a simple index (1, 2, 3, ...)")
- Numeric IDs are intuitive for CLI users (easy to type, remember, reference)
- Never reusing IDs prevents user confusion ("wait, is this the same task that was deleted earlier?")
- Next available ID (`next_id`) tracked separately in JSON ensures correctness
- Simpler than UUID/GUID approaches while maintaining uniqueness

**Alternatives Considered**:
- **UUID/GUID**: Cryptographically unique, but unfriendly for CLI users; overkill for local, single-user app
- **Array indices**: Change when tasks deleted (poor UX; users reference by old index)
- **Timestamp-based**: Difficult to type, conflicts possible
- **Sequential reuse**: Violates principle of never reusing IDs; confusing for users

**Conclusion**: ✅ Auto-incrementing numeric IDs selected; specification-aligned and user-friendly

---

### 4. Command Dispatch Architecture

**Question**: How should CLI commands be parsed and dispatched?

**Decision**: Standard `argparse` library with subcommand pattern

**Rationale**:
- `argparse` is standard library (Python 3.8+); no external dependencies
- Subcommand pattern is Unix standard (`git commit`, `docker run`, `aws ec2 describe`)
- Familiar to users; low learning curve
- Built-in help generation and error handling
- Easily extensible for future commands
- Clean separation of command logic in `commands.py`

**Alternatives Considered**:
- **Click**: Popular framework, but adds 2+ external dependencies (click, colorama)
- **Typer**: Modern, but requires FastAPI ecosystem (overkill)
- **Manual argparse**: More verbose; click/typer libraries better abstractions
- **Positional arguments only**: No help/error validation; poor UX
- **Environment variables**: Violates Unix principle; harder to discover

**Conclusion**: ✅ Standard `argparse` with subcommands selected for simplicity and no dependencies

---

### 5. Persistence Model

**Question**: Should tasks be loaded on-demand, lazy-loaded, or fully cached?

**Decision**: Full in-memory load on startup; persist after each mutation

**Rationale**:
- Task lists are small (<1MB for 1000+ tasks); trivial memory footprint
- Fast lookups (O(n) in-memory vs. O(1) with indexing, but n is tiny)
- No complex locking needed (single-user, sequential CLI)
- Safe by design: data always persisted after mutation
- Simplest implementation; easiest to test and debug
- Meets performance requirement (<1 second response time)

**Alternatives Considered**:
- **Lazy loading**: More complex; not needed for small datasets
- **Database with connection pooling**: Overkill; adds framework dependencies
- **Distributed cache (Redis)**: Completely unnecessary for local, single-user app
- **Memory-mapped files**: Unnecessary complexity; standard JSON I/O sufficient

**Conclusion**: ✅ Full cache on startup with immediate persistence selected

---

### 6. Error Handling Strategy

**Question**: How should errors be reported to users?

**Decision**: Custom exception hierarchy with human-readable error messages

**Rationale**:
- FR-006 requires clear error messages for invalid task IDs
- Custom exceptions enable consistent error handling across all commands
- Human-readable messages guide users to correct behavior
- Testable error scenarios in unit tests
- No stack traces in production (stderr shows only message)

**Exception Types**:
- `TaskNotFoundError`: Task ID doesn't exist
- `InvalidTaskError`: Empty description or invalid data
- `StorageError`: File I/O failures
- `CommandError`: Invalid command arguments

**Alternatives Considered**:
- **Generic exceptions**: Less informative; harder to test specific scenarios
- **Silent failures**: Violates specification requirement for clear messages
- **Exit codes only**: Impossible for user to understand what went wrong

**Conclusion**: ✅ Custom exception hierarchy with user-friendly messages selected

---

### 7. Testing Framework

**Question**: What framework should be used for automated testing?

**Decision**: `pytest` with standard fixtures and parametrization

**Rationale**:
- `pytest` is Python standard for modern testing
- Simpler syntax than `unittest` (pytest alternative in stdlib)
- Built-in fixtures and parametrization reduce boilerplate
- Rich assertion introspection (helpful error messages)
- Community standard; widely used in Python ecosystem

**Alternative Testing**:
- **unittest (stdlib)**: Verbose, class-based; older style
- **nose**: Deprecated in favor of pytest
- **tox**: Multiple environment testing; overkill for single-user app

**Conclusion**: ✅ `pytest` selected; standard practice in Python projects

---

### 8. Configuration and Defaults

**Question**: Should the application support configuration files or environment variables?

**Decision**: Minimal configuration; use sensible defaults only

**Rationale**:
- Specification constraints don't mention customization requirements
- YAGNI principle: Don't add features users haven't requested
- Single-user, local-only app; no multi-environment concerns
- Tasks stored in standard location (`~/.todo/tasks.json`)
- Users can manually edit JSON if needed
- Reduces code complexity and testing burden

**Possible Future Configurations** (not in MVP):
- Custom storage location (env var `TODO_HOME`)
- Output formatting preferences (JSON, CSV, table)
- Completion indicator style (checkmark, cross, label)

**Conclusion**: ✅ No configuration; sensible defaults only for MVP

---

### 9. Backward Compatibility

**Question**: How should schema evolution be handled as the app evolves?

**Decision**: Version schema in JSON; plan for forward compatibility

**Rationale**:
- `version` field in JSON enables future schema changes
- Current schema: `version: 1`
- Code checks version on load; can handle multiple versions if needed
- Optional fields (timestamps) support gradual feature rollout

**Forward Compatibility Plan**:
- Task model includes `created_at`, `updated_at` (optional, used in v1+)
- Future versions can add fields without breaking existing data
- Example: v2 adds `priority: int` field; v2 code can read v1 files

**Conclusion**: ✅ Versioned schema with forward-compatible design selected

---

## Summary of Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.8+ | Ubiquitous, simple, zero dependencies |
| Storage | JSON file | Human-readable, zero dependencies |
| Task IDs | Auto-increment, never reuse | User-friendly, spec-compliant |
| CLI | argparse + subcommands | Unix standard, zero dependencies |
| Persistence | Full cache + immediate save | Simple, safe, fast enough |
| Errors | Custom exceptions + messages | Testable, user-friendly |
| Testing | pytest | Python standard |
| Config | Sensible defaults, no config | YAGNI principle |
| Schema | Versioned, forward-compatible | Enables safe evolution |

---

## Architectural Principles

1. **Zero Dependencies**: Use only Python standard library (except pytest for testing)
2. **Single User**: No concurrency, locking, or multi-user concerns
3. **Simplicity**: Minimal code; YAGNI; prefer small modules
4. **Clarity**: Code is readable and maintainable
5. **Testability**: All logic is unit-testable
6. **Safety**: Data never lost; atomic operations where possible
7. **Unix Philosophy**: Fits with standard command-line tools and conventions

---

## Risks and Mitigations

### Risk 1: File Corruption on App Crash

**Impact**: Data loss if app crashes during JSON write

**Mitigation**:
- Use atomic writes: write to temp file, then rename
- Python's `pathlib` and `json.dump()` handle this automatically
- Testing includes crash-during-write scenarios

### Risk 2: Schema Mismatch

**Impact**: Confusion if schema changes without notice

**Mitigation**:
- Version field in JSON (`version: 1`)
- Code checks version on load
- Clear error if version mismatch detected

### Risk 3: Performance Degradation with Large Task Lists

**Impact**: Slowdown with 10,000+ tasks

**Mitigation**:
- In-memory storage is O(1) for list operations
- Even 100,000 tasks = <10MB memory (negligible)
- If performance becomes issue, can add simple indexing
- Specification doesn't mention 10k+ tasks; MVP targets <1000

### Risk 4: Data Format Brittleness

**Impact**: Manual JSON editing could corrupt data

**Mitigation**:
- Clear documentation about manual editing (not recommended)
- Validation on load detects and reports corruption
- Users can restore from backup

---

## Future Considerations

These are NOT included in MVP but guide design decisions:

1. **Task Categories/Tags**: Add `tags: list[str]` to Task
2. **Task Priorities**: Add `priority: int` (1-5) to Task
3. **Due Dates**: Add `due_at: ISO8601 timestamp` to Task
4. **Recurring Tasks**: Add `recurrence: str` (daily, weekly, etc.) to Task
5. **Task Notes**: Add `notes: str` to Task
6. **Archival**: Keep deleted tasks in separate collection for history
7. **Multi-user Sync**: SQLite + cloud sync (Dropbox, etc.)
8. **Dark Mode**: Terminal color schemes based on environment
9. **Bash Completion**: Shell auto-completion for task IDs
10. **Undo/Redo**: Operation history for reversible actions

Current design supports all of these without schema changes (add optional fields).

---

## Conclusion

The selected architecture balances simplicity with specification requirements. By using Python's standard library and simple JSON storage, we eliminate dependency management, deployment complexity, and learning curve. The modular design (models, storage, commands, formatting) enables testability and future extensibility while keeping the MVP focused and deployable.

**Status**: ✅ Research complete; ready for Phase 1 design work
