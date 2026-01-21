<!-- Sync Impact Report:
Version change: 0.1.0 → 0.2.0
Modified principles: Added Phase IV Deployment principles (VIII, IX)
Added sections: VIII. Phase IV Deployment Requirements, IX. Container Orchestration Standards
Removed sections: None
Templates requiring updates: ✅ updated - .specify/templates/plan-template.md, ⚠ pending - .specify/templates/spec-template.md, .specify/templates/tasks-template.md
Follow-up TODOs: None
-->

# AI-Powered Todo Chatbot Constitution

## Core Principles

### I. Stateless Architecture (MUST)

All server state is stored exclusively in the database. No in-memory caches, sessions, or runtime state persists beyond request lifecycle. Every request is independently processable. Database is the single source of truth.

**Rationale**: Stateless design enables horizontal scaling, fault tolerance, and simplifies testing. MCP-based agents are inherently ephemeral; databases ensure consistency across agent instances and request batches.

### II. Spec-Driven Development (MUST)

All development follows the rigid workflow: Specify → Plan → Tasks → Implement. No manual coding, changes, or deployments occur outside this workflow. Each stage has formal artifacts (spec.md, plan.md, tasks.md). User approval gates each stage.

**Rationale**: Formal specification prevents ambiguity, ensures traceability, and maintains architectural coherence. MCP agents operate within documented contracts; deviation breaks predictability.

### III. MCP-First Tool Integration (MUST)

All external interactions use Model Context Protocol (MCP) servers. Tools, APIs, and system capabilities are exposed via MCP. Agents discover and invoke tools through MCP contracts. No hardcoded API calls; all interactions are tool-mediated.

**Rationale**: MCP provides a unified interface for agents to reason about and use tools safely. This decouples agent logic from implementation details and enables tool composability.

### IV. Agent SDK Compliance (MUST)

All agent behavior conforms to OpenAI Agents SDK patterns and ChatKit library semantics. Agents are stateless; logic lives in tools (MCP) or persistent schemas (database). No agent-local state between requests.

**Rationale**: Agents are powerful but require discipline. SDK compliance ensures reproducible, auditable agent behavior and simplifies debugging and scaling.

### V. Database-Driven State (MUST)

All mutable state resides in the database schema. Todos, user preferences, conversation history, and agent metadata are persisted. Schema changes require migration planning. No assumption of schema immutability.

**Rationale**: Persistence enables audit trails, historical queries, and recovery. Migrations formalize schema evolution and reduce breakage risk.

### VI. Test-First Implementation (MUST)

Before any code is written, acceptance tests are defined and approved by the user. Tests drive implementation. Red-Green-Refactor cycle is enforced. Integration tests validate MCP tool contracts and database interactions. No untested code ships.

**Rationale**: Tests serve as executable specifications. TDD ensures contracts are met before implementation details diverge.

### VII. Simplicity Over Abstraction (MUST)

Start simple. Avoid premature abstraction, configuration, or "future-proofing." Use YAGNI (You Aren't Gonna Need It). One-off functions are better than generic utilities. Concrete is preferred over abstract until duplication forces refactoring.

**Rationale**: Simpler code is faster to write, easier to debug, and cheaper to maintain. Premature abstraction obscures intent and delays shipping.

### VIII. Phase IV Deployment Requirements (MUST)

Phase III code is read-only. Only Docker, Helm, and Kubernetes-related files may be added during Phase IV. No manual coding by the user. All deployment activities must align with Phase IV requirements only.

**Rationale**: Maintaining Phase III stability while enabling safe deployment through containerization and orchestration. This ensures backward compatibility while enabling modern deployment practices.

### IX. Container Orchestration Standards (MUST)

Deployment infrastructure must use Docker for containerization, Helm for packaging, and Kubernetes for orchestration. Local deployment targets Minikube exclusively. Prefer AI-assisted tools (Docker AI, kubectl-ai, kagent) when available; fall back to standard Docker commands when AI tools unavailable. Keep deployments minimal and explainable.

**Rationale**: Standardized container orchestration ensures consistent deployment across environments. AI-assisted tools accelerate development while maintaining reliability. Minikube provides safe local testing without cloud dependencies.

## Architecture and Technology

### Stack

- **Framework**: OpenAI Agents SDK (Python/TypeScript as per project conventions)
- **Chat Interface**: ChatKit library
- **Tool Layer**: Model Context Protocol (MCP) servers
- **Database**: PostgreSQL (as established in Phase III)
- **Agent Pattern**: Stateless request-response; state lives in DB and MCP tool responses
- **Containerization**: Docker
- **Orchestration**: Kubernetes (Minikube for local)
- **Packaging**: Helm charts

### Non-Functional Requirements

- **Availability**: Server must be restartable without data loss (database persists all state).
- **Scalability**: Horizontal scaling supported; all requests are independent.
- **Security**: MCP tools validate inputs; no secrets in code; use environment variables.
- **Observability**: All agent calls, tool invocations, and database writes are logged with request IDs for tracing.
- **Deployability**: Applications must be deployable via Helm charts to Kubernetes clusters.

## Development Workflow

### Stages

1. **Specify** (spec.md): User describes the feature in plain language; team formalizes user stories, acceptance criteria, and edge cases.
2. **Plan** (plan.md): Architect designs MCP tool contracts, database schema changes, and agent logic flow. Documents tradeoffs and alternatives. For Phase IV, includes containerization and orchestration plans.
3. **Tasks** (tasks.md): Break plan into small, testable, independently executable tasks. Each task includes acceptance tests. For Phase IV, includes deployment-related tasks.
4. **Implement** (via `sp.implement` skill): Execute tasks in order. Tests must pass. Code is reviewed against tasks and architecture. No scope creep.

### Quality Gates

- **Spec Gate**: User approves user stories and acceptance criteria before planning begins.
- **Plan Gate**: Architecture decisions are documented; ADRs created for significant choices. User approves design before tasks are written.
- **Task Gate**: Acceptance tests are approved before implementation starts.
- **Impl Gate**: All tests pass. Code is traceable to tasks. No unrelated changes.

### Code Review Checklist

- Implemented to task spec exactly (no scope creep).
- All acceptance tests pass.
- MCP tool contracts honored.
- Database state changes logged and reversible.
- No hardcoded secrets or environment-specific values.
- Stateless server assumption maintained.
- Phase III code remains unchanged during Phase IV.
- Docker, Helm, and Kubernetes files properly structured.

## Governance

### Constitution Supremacy

This constitution supersedes all other project guidance. If a practice conflicts with a principle, the principle wins. Exceptions require documented ADRs and explicit user approval.

### Amendment Process

1. Propose amendment with rationale (what changed, why, impact on templates).
2. User approves amendment.
3. Increment version (MAJOR for incompatible changes, MINOR for additions, PATCH for clarifications).
4. Update dependent templates:
   - `.specify/templates/spec-template.md`
   - `.specify/templates/plan-template.md`
   - `.specify/templates/tasks-template.md`
   - `CLAUDE.md` runtime guidance (if needed)
5. Record amendment in Sync Impact Report.

### Compliance Review

All PRs must verify:
- No code outside Specify → Plan → Tasks → Implement workflow.
- No in-memory state in server logic.
- All MCP tool invocations are intentional and logged.
- Database schema changes have migration scripts.
- Tests cover acceptance criteria from spec.
- Phase III code remains unchanged during Phase IV.
- All deployment changes follow container orchestration standards.

### Prompt History Records (PHRs)

Every user prompt and corresponding work is recorded as a PHR in `history/prompts/` under the appropriate stage directory. PHRs capture:
- Full user input (verbatim, not truncated).
- Key decisions and outputs.
- Files modified and tests run.
- Rationale for significant choices.

PHRs serve as audit trail and enable learning loops.

### Architectural Decision Records (ADRs)

Significant architectural decisions (framework choices, MCP tool design, database schema, agent patterns) are documented in ADRs under `history/adr/`. Each ADR captures:
- Context: problem, constraints, stakeholders.
- Decision: what was chosen.
- Rationale: why this option over alternatives.
- Consequences: short- and long-term implications.
- Status: Proposed, Accepted, Deprecated, Superseded.

**Version**: 0.3.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2026-01-21

## Phase IV Completion

### Phase IV Requirements Met

✅ **Containerization**: Docker images for frontend and backend
✅ **Helm Charts**: Complete Helm chart for deployment management
✅ **Kubernetes Deployment**: Running on local Minikube cluster
✅ **Docker AI (Gordon)**: Used for intelligent Docker operations
✅ **kubectl-ai/kagent**: Used for AI-assisted Kubernetes operations
✅ **Local Deployment**: Minikube-based local Kubernetes cluster
✅ **Working Application**: Fully functional Todo Chatbot with chat capabilities
✅ **Phase III Code Preservation**: No changes to application logic during Phase IV
