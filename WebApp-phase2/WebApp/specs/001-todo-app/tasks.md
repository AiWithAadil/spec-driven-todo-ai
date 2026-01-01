---
description: "Implementation tasks for web-based todo application"
---

# Tasks: Web-based Todo Application

**Input**: Design documents from `/specs/001-todo-app/`
**Prerequisites**: plan.md (architecture), spec.md (user stories), research.md (tech decisions), data-model.md (schema), contracts/openapi.yaml (API spec)

**Organization**: Tasks grouped by user story (US1-US7) to enable independent, parallel implementation and testing.

**MVP Scope**: Complete Setup → Foundational → User Stories 1-4 (registration, login, view tasks, add tasks)

---

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[TaskID]**: Sequential (T001, T002, etc.)
- **[P]**: Parallelizable (different files/modules, no blocking dependencies)
- **[Story]**: User story label (US1, US2, etc.) for story-specific tasks only
- **File paths**: Exact location of file to create/modify

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

**Duration**: ~1-2 hours

- [ ] T001 Create backend directory structure: `backend/app/`, `backend/tests/`, per plan.md
- [ ] T002 Create frontend directory structure: `frontend/app/`, `frontend/components/`, `frontend/services/`, per plan.md
- [ ] T003 [P] Create Python virtual environment in `backend/venv/` and install dependencies from requirements.txt
- [ ] T004 [P] Initialize Node.js project in `frontend/` with `npm install` and tsconfig.json configuration
- [ ] T005 [P] Create `.env.example` files in both `backend/` and `frontend/` with required environment variables
- [ ] T006 [P] Configure `.gitignore` to exclude venv/, node_modules/, .env, __pycache__/, .next/
- [ ] T007 Create `docker-compose.yml` at repository root with PostgreSQL, backend, and frontend services
- [ ] T008 Create initial `README.md` at repository root with project overview and setup instructions
- [ ] T009 [P] Configure backend: `backend/app/__init__.py`, `backend/app/config.py` for environment management
- [ ] T010 [P] Configure frontend: `frontend/next.config.ts`, `frontend/tsconfig.json` for TypeScript support

**Checkpoint**: Project structure ready, dependencies installed, environment configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure REQUIRED before any user story implementation

**⚠️ CRITICAL**: All tasks in this phase must complete before user story work begins

**Duration**: ~3-4 hours

### Database & ORM Setup

- [ ] T011 Create SQLAlchemy models base class in `backend/app/database.py` with engine, session factory, and declarative base
- [ ] T012 [P] Create User model in `backend/app/models.py`: id, email (unique), hashed_password, created_at
- [ ] T013 [P] Create Task model in `backend/app/models.py`: id, user_id (FK), title, description, is_completed, created_at, updated_at
- [ ] T014 Create Alembic migration framework: `backend/alembic/` directory with env.py, script.py.mako
- [ ] T015 Generate initial Alembic migration for User and Task tables: `backend/alembic/versions/001_initial_schema.py`

### API Foundation & Middleware

- [ ] T016 Create FastAPI application in `backend/app/main.py` with CORS, error handling, logging setup
- [ ] T017 [P] Implement authentication middleware in `backend/app/utils/security.py`: JWT token generation, verification, bcrypt hashing
- [ ] T018 [P] Create Pydantic schemas in `backend/app/schemas.py`:
  - UserSchema, UserRegisterSchema, UserLoginSchema, UserResponseSchema
  - TaskSchema, TaskCreateSchema, TaskUpdateSchema
- [ ] T019 Create error handling utilities in `backend/app/utils/errors.py`: custom exception classes, error responses
- [ ] T020 Setup FastAPI dependency injection in `backend/app/dependencies.py` for database session, current user

### Frontend Foundation & State Management

- [ ] T021 Create Auth Context in `frontend/context/AuthContext.tsx`: user state, login, logout, register actions
- [ ] T022 [P] Create Task Context in `frontend/context/TaskContext.tsx`: tasks list, add, update, delete, complete actions
- [ ] T023 [P] Create custom hooks: `frontend/hooks/useAuth.ts` (auth state/actions), `frontend/hooks/useTasks.ts` (task state/actions)
- [ ] T024 [P] Create API client service in `frontend/services/api.ts`: fetch wrapper with Bearer token, error handling, base URL
- [ ] T025 [P] Create type definitions in `frontend/types/auth.ts` and `frontend/types/task.ts`: User, Task, Login/Register requests
- [ ] T026 Create layout components in `frontend/components/Header.tsx`: navigation, logout button, responsive design setup
- [ ] T027 Create global styles in `frontend/styles/globals.css`: clean minimal design (no flashy colors), responsive breakpoints
- [ ] T028 Create root layout in `frontend/app/layout.tsx`: auth context provider, task context provider, header component

### Testing Infrastructure (OPTIONAL - Setup only, tests per user story)

- [ ] T029 [P] Setup pytest configuration: `backend/pytest.ini`, `backend/tests/conftest.py` with database fixtures
- [ ] T030 [P] Setup Jest configuration: `frontend/jest.config.js`, `frontend/__mocks__/` for API mocking

**Checkpoint**: Foundation complete - all infrastructure ready, database schema created, API & frontend frameworks initialized. User story implementation can now begin.

---

## Phase 3: User Story 1 - User Registration and Account Creation (Priority: P1)

**Goal**: Enable new users to create accounts with email and password, with proper validation and duplicate prevention

**Spec Reference**: [User Story 1](spec.md#user-story-1---user-registration-and-account-creation-priority-p1)

**Independent Test**: Create account with valid email/password → verify account exists → login with same credentials succeeds

**API Contract**: `POST /api/v1/auth/register` (request: email, password, password_confirm; response: access_token, user)

### Implementation for User Story 1

#### Backend Tasks

- [ ] T031 [P] [US1] Create UserService in `backend/app/services/user_service.py`: register method with email validation, password hashing, duplicate check
- [ ] T032 [US1] Implement registration endpoint `POST /api/v1/auth/register` in `backend/app/api/auth.py`:
  - Accept email, password, password_confirm
  - Validate: email format, passwords match, no duplicates
  - Hash password with bcrypt
  - Create User, return JWT token and user object
  - Error responses: 400 (validation), 409 (duplicate email)
- [ ] T033 [P] [US1] Create auth validation utilities in `backend/app/utils/validation.py`: email format, password strength, password confirmation

#### Frontend Tasks

- [ ] T034 [P] [US1] Create registration API service in `frontend/services/auth.ts`: register function calling POST /api/v1/auth/register
- [ ] T035 [US1] Create registration form component in `frontend/components/RegisterForm.tsx`:
  - Email input field with validation
  - Password input field
  - Password confirmation input field
  - Submit button
  - Error message display
  - Loading state during submission
- [ ] T036 [US1] Create registration page in `frontend/app/auth/register/page.tsx`:
  - Display RegisterForm component
  - Handle successful registration: store token, redirect to dashboard
  - Handle errors: display validation errors
  - Link to login page for existing users
- [ ] T037 [P] [US1] Update AuthContext in `frontend/context/AuthContext.tsx`: add register action calling backend API
- [ ] T038 [P] [US1] Create form validation utilities in `frontend/utils/validation.ts`: email format, password strength, password match

#### Integration Tasks

- [ ] T039 [US1] Integration test: Register new user in browser → verify redirect to dashboard → verify token stored locally
- [ ] T040 [US1] Integration test: Attempt register with duplicate email → verify error message displayed
- [ ] T041 [US1] Integration test: Attempt register with invalid email → verify validation error before submission
- [ ] T042 [US1] Database verification: Query users table → confirm new user exists with hashed password

**Checkpoint**: User registration fully functional. Users can create accounts, passwords are hashed, duplicates rejected, token issued.

---

## Phase 4: User Story 2 - User Login with JWT Authentication (Priority: P1)

**Goal**: Enable existing users to authenticate with email and password, receive JWT token, maintain session across page refreshes

**Spec Reference**: [User Story 2](spec.md#user-story-2---user-login-with-jwt-authentication-priority-p1)

**Independent Test**: Login with valid credentials → receive token → navigate away and back → still authenticated without re-login

**API Contract**: `POST /api/v1/auth/login` (request: email, password; response: access_token, user)

### Implementation for User Story 2

#### Backend Tasks

- [ ] T043 [P] [US2] Create login method in `backend/app/services/user_service.py`: find user by email, verify password with bcrypt
- [ ] T044 [US2] Implement login endpoint `POST /api/v1/auth/login` in `backend/app/api/auth.py`:
  - Accept email, password
  - Verify user exists and password matches
  - Generate JWT token with 7-day expiration
  - Return token and user object
  - Error response: 401 (invalid credentials)
- [ ] T045 [P] [US2] Create JWT utilities in `backend/app/utils/security.py`: create_access_token function with user_id, email, expiration

#### Frontend Tasks

- [ ] T046 [P] [US2] Create login API service in `frontend/services/auth.ts`: login function calling POST /api/v1/auth/login
- [ ] T047 [US2] Create login form component in `frontend/components/LoginForm.tsx`:
  - Email input field
  - Password input field
  - Submit button
  - Error message display
  - Loading state during submission
- [ ] T048 [US2] Create login page in `frontend/app/auth/login/page.tsx`:
  - Display LoginForm component
  - Handle successful login: store token in localStorage, redirect to dashboard
  - Handle errors: display "invalid credentials" message
  - Link to registration page for new users
- [ ] T049 [P] [US2] Update AuthContext in `frontend/context/AuthContext.tsx`: add login action calling backend API
- [ ] T050 [US2] Implement token persistence in `frontend/services/auth.ts`: store token in localStorage on login, retrieve on app load
- [ ] T051 [US2] Create protected route wrapper in `frontend/utils/protectedRoute.ts`: redirect to login if no token, check token validity

#### Session Management Tasks

- [ ] T052 [P] [US2] Add token to requests in `frontend/services/api.ts`: automatically add "Authorization: Bearer" header to all requests using token from localStorage
- [ ] T053 [US2] Implement logout in `frontend/context/AuthContext.tsx`: clear token from localStorage, clear auth state, redirect to login
- [ ] T054 [US2] Add logout button to `frontend/components/Header.tsx`: call logout action, ensure redirection to login page

#### Integration Tasks

- [ ] T055 [US2] Integration test: Login with valid credentials → verify token received and stored → verify redirect to dashboard
- [ ] T056 [US2] Integration test: Login with invalid password → verify error message displayed
- [ ] T057 [US2] Integration test: Login → refresh page → verify still authenticated without re-login
- [ ] T058 [US2] Integration test: Login → click logout → verify redirected to login page, token cleared from localStorage

**Checkpoint**: User authentication fully functional. Login works, tokens issued and persisted, session maintains across refreshes, logout clears session.

---

## Phase 5: User Story 3 - View Tasks on Dashboard (Priority: P1)

**Goal**: Display user's complete task list on clean dashboard with proper organization, empty state, and responsive design

**Spec Reference**: [User Story 3](spec.md#user-story-3---view-tasks-on-dashboard-priority-p1)

**Independent Test**: Login → navigate to dashboard → all tasks display with title, status, creation date → empty state shows if no tasks → responsive on mobile

**API Contract**: `GET /api/v1/tasks` (requires auth; response: array of Task objects)

### Implementation for User Story 3

#### Backend Tasks

- [ ] T059 [P] [US3] Create task listing method in `backend/app/services/task_service.py`: get_user_tasks(user_id) returning all user's tasks ordered by created_at DESC
- [ ] T060 [US3] Implement list tasks endpoint `GET /api/v1/tasks` in `backend/app/api/tasks.py`:
  - Require authentication (extract user_id from JWT token)
  - Return all tasks for authenticated user
  - Success response: { "tasks": [...], "total": N }
  - Error response: 401 (unauthorized)

#### Frontend Tasks

- [ ] T061 [P] [US3] Create task list service in `frontend/services/tasks.ts`: fetchTasks function calling GET /api/v1/tasks
- [ ] T062 [P] [US3] Create TaskItem component in `frontend/components/TaskItem.tsx`:
  - Display task title, description, creation date
  - Show completion status with visual indicator (checkbox, strikethrough for completed)
  - Responsive layout with proper spacing
- [ ] T063 [P] [US3] Create TaskList component in `frontend/components/TaskList.tsx`:
  - Display array of tasks using TaskItem components
  - Sort by creation date (newest first)
  - Distinguish completed vs incomplete tasks visually
- [ ] T064 [US3] Create empty state component in `frontend/components/EmptyState.tsx`:
  - Display when task list is empty
  - Show message: "No tasks yet. Create one to get started!"
  - Include link/button to create first task
- [ ] T065 [US3] Create dashboard page in `frontend/app/dashboard/page.tsx`:
  - Fetch tasks on page load using useTasksContext
  - Display TaskList or EmptyState based on whether tasks exist
  - Add loading state while fetching
  - Handle API errors gracefully
- [ ] T066 [P] [US3] Create dashboard layout in `frontend/app/dashboard/layout.tsx`:
  - Include Header component with user name and logout button
  - Add sidebar or navbar with navigation
  - Ensure responsive design (hamburger menu on mobile)
- [ ] T067 [US3] Update root layout: redirect "/" to "/dashboard" if authenticated, to "/auth/login" if not
- [ ] T068 [P] [US3] Implement responsive styling in `frontend/styles/globals.css` and component styles:
  - Mobile breakpoint (320px): single column, touch-friendly buttons
  - Tablet breakpoint (768px): optimized spacing
  - Desktop breakpoint (1024px+): full width with proper margins
  - Clean typography (no flashy colors, muted grays/blacks)

#### State Management Tasks

- [ ] T069 [US3] Update TaskContext in `frontend/context/TaskContext.tsx`: add tasks state, setTasks action
- [ ] T070 [US3] Add fetchTasks action to TaskContext: call tasks.ts service, update state
- [ ] T071 [P] [US3] Update useTasks hook in `frontend/hooks/useTasks.ts`: provide tasks state and fetchTasks action

#### Integration Tasks

- [ ] T072 [US3] Integration test: Login → navigate to /dashboard → verify all tasks display with correct data
- [ ] T073 [US3] Integration test: Login with no tasks → navigate to /dashboard → verify empty state message displays
- [ ] T074 [US3] Integration test: View dashboard on mobile (320px) → verify responsive layout works, content readable
- [ ] T075 [US3] Integration test: View dashboard on tablet (768px) → verify spacing and layout optimized
- [ ] T076 [US3] Integration test: Verify no flashy colors used, clean minimal design (similar to Notion/Linear)

**Checkpoint**: Dashboard fully functional. Users can view all their tasks, empty state displays when appropriate, responsive design works across devices, clean minimal UI.

---

## Phase 6: User Story 4 - Add New Task (Priority: P1)

**Goal**: Enable users to create new tasks with title and optional description, immediately visible on dashboard

**Spec Reference**: [User Story 4](spec.md#user-story-4---add-new-task-priority-p1)

**Independent Test**: Dashboard → click "Add Task" → enter title → task appears immediately in list and persists after refresh

**API Contract**: `POST /api/v1/tasks` (requires auth; request: title, description; response: Task object)

### Implementation for User Story 4

#### Backend Tasks

- [ ] T077 [P] [US4] Create task creation method in `backend/app/services/task_service.py`: create_task(user_id, title, description)
- [ ] T078 [US4] Implement create task endpoint `POST /api/v1/tasks` in `backend/app/api/tasks.py`:
  - Require authentication
  - Accept title (required), description (optional)
  - Validate: title non-empty, max 255 characters
  - Create Task with user_id, initial is_completed=False
  - Return created task object
  - Error responses: 400 (validation), 401 (unauthorized)

#### Frontend Tasks

- [ ] T079 [P] [US4] Create task creation service in `frontend/services/tasks.ts`: createTask function calling POST /api/v1/tasks
- [ ] T080 [P] [US4] Create TaskForm component in `frontend/components/TaskForm.tsx`:
  - Title input field (required, max 255 chars)
  - Description textarea (optional, max 10000 chars)
  - Submit button ("Add Task")
  - Cancel button
  - Character counter for title
  - Error message display
  - Loading state during submission
- [ ] T081 [US4] Add TaskForm to dashboard page in `frontend/app/dashboard/page.tsx`:
  - Display at top of task list or in modal
  - On submit: call createTask API
  - On success: add new task to TaskList, clear form
  - On error: display error message
- [ ] T082 [P] [US4] Update TaskContext in `frontend/context/TaskContext.tsx`: add createTask action
- [ ] T083 [US4] Create form submission handler in `frontend/components/TaskForm.tsx`:
  - Validate title non-empty before submit
  - Call useTasksContext.createTask
  - Clear form after successful submission
  - Display error if submission fails

#### Integration Tasks

- [ ] T084 [US4] Integration test: Dashboard → click "Add Task" → enter valid title → task appears immediately in list
- [ ] T084 [US4] Integration test: Add task → refresh page → verify task persists in database and displays
- [ ] T085 [US4] Integration test: Attempt to add task with empty title → verify validation error before submission
- [ ] T086 [US4] Integration test: Add task with title and description → verify both fields saved and displayed correctly
- [ ] T087 [US4] Integration test: Add task → form clears → can add another task without page refresh

**Checkpoint**: Task creation fully functional. Users can add tasks with title and optional description, tasks appear immediately, form resets, data persists.

---

## Phase 7: User Story 5 - Mark Task as Complete (Priority: P2)

**Goal**: Enable users to toggle task completion status with visual feedback

**Spec Reference**: [User Story 5](spec.md#user-story-5---mark-task-as-complete-priority-p2)

**Independent Test**: Task in list → click checkbox → status changes to complete → visual indicator shows (strikethrough) → refresh → still marked complete

**API Contract**: `PATCH /api/v1/tasks/{id}` (requires auth; request: is_completed=bool; response: Task object)

### Implementation for User Story 5

#### Backend Tasks

- [ ] T088 [P] [US5] Create task update method in `backend/app/services/task_service.py`: update_task_status(user_id, task_id, is_completed)
- [ ] T089 [US5] Implement partial update endpoint `PATCH /api/v1/tasks/{task_id}` in `backend/app/api/tasks.py`:
  - Require authentication
  - Accept is_completed (boolean) in request body
  - Verify user owns task (check user_id)
  - Update task is_completed and updated_at timestamp
  - Return updated task object
  - Error responses: 400 (invalid), 401 (unauthorized), 403 (not owner), 404 (not found)

#### Frontend Tasks

- [ ] T090 [P] [US5] Create task update service in `frontend/services/tasks.ts`: updateTask function calling PATCH /api/v1/tasks/{id}
- [ ] T091 [US5] Add checkbox to TaskItem component in `frontend/components/TaskItem.tsx`:
  - Checkbox input reflecting is_completed status
  - On change: call updateTask API
  - On success: update local state, show visual feedback
  - On error: revert checkbox, display error message
- [ ] T092 [P] [US5] Add visual styling for completed tasks in `frontend/components/TaskItem.tsx` and `frontend/styles/globals.css`:
  - Strikethrough text for completed tasks
  - Muted color (gray) for completed tasks
  - Different background or border for visual distinction
- [ ] T093 [US5] Update TaskContext in `frontend/context/TaskContext.tsx`: add updateTask action
- [ ] T094 [P] [US5] Update useTasks hook in `frontend/hooks/useTasks.ts`: provide updateTask action

#### Integration Tasks

- [ ] T095 [US5] Integration test: Task in list → click checkbox → status changes to complete → strikethrough appears
- [ ] T096 [US5] Integration test: Completed task → click checkbox again → status reverts to incomplete, strikethrough removed
- [ ] T097 [US5] Integration test: Mark task complete → refresh page → verify still marked complete in database
- [ ] T098 [US5] Integration test: Dashboard with mixed completed/incomplete tasks → verify all visually distinguishable

**Checkpoint**: Task completion toggle fully functional. Users can mark tasks complete/incomplete, visual feedback immediate, status persists.

---

## Phase 8: User Story 6 - Update Task (Priority: P2)

**Goal**: Enable users to edit task title and description

**Spec Reference**: [User Story 6](spec.md#user-story-6---update-task-priority-p2)

**Independent Test**: Task in list → click edit → change title/description → save → changes appear immediately and persist

**API Contract**: `PUT /api/v1/tasks/{id}` (requires auth; request: title, description, is_completed; response: Task object)

### Implementation for User Story 6

#### Backend Tasks

- [ ] T099 [P] [US6] Create task edit method in `backend/app/services/task_service.py`: update_task(user_id, task_id, title, description, is_completed)
- [ ] T100 [US6] Implement update endpoint `PUT /api/v1/tasks/{task_id}` in `backend/app/api/tasks.py`:
  - Require authentication
  - Accept title, description, is_completed in request body
  - Validate: title non-empty, max 255 characters
  - Verify user owns task
  - Update task fields and updated_at timestamp
  - Return updated task object
  - Error responses: 400 (validation), 401 (unauthorized), 403 (not owner), 404 (not found)

#### Frontend Tasks

- [ ] T101 [P] [US6] Create task edit service in `frontend/services/tasks.ts`: updateTask function calling PUT /api/v1/tasks/{id}
- [ ] T102 [US6] Extend TaskItem component with edit mode in `frontend/components/TaskItem.tsx`:
  - Add edit button to task item
  - On click: switch to edit mode showing input fields
  - Display title and description in editable fields
  - Show save and cancel buttons
  - Validate before save (title non-empty)
- [ ] T103 [P] [US6] Create edit form logic in `frontend/components/TaskItem.tsx`:
  - Store edit state locally
  - On save: call updateTask API with modified values
  - On cancel: discard changes, revert to view mode
  - On success: update local state, return to view mode
  - On error: display error, keep edit mode
- [ ] T104 [US6] Update TaskContext in `frontend/context/TaskContext.tsx`: add updateTask action (shared with US5)
- [ ] T105 [P] [US6] Update useTasks hook in `frontend/hooks/useTasks.ts`: ensure updateTask action available

#### Integration Tasks

- [ ] T106 [US6] Integration test: Task in list → click edit → change title → save → title updates immediately and persists
- [ ] T107 [US6] Integration test: Edit task → change description → save → description updates and displays correctly
- [ ] T108 [US6] Integration test: Edit task → click cancel → changes discarded, original values display
- [ ] T109 [US6] Integration test: Attempt to save with empty title → verify validation error, edit mode maintained
- [ ] T110 [US6] Integration test: Edit task → refresh page → verify changes persisted in database

**Checkpoint**: Task editing fully functional. Users can modify title and description, changes persist, validation prevents empty titles.

---

## Phase 9: User Story 7 - Delete Task (Priority: P2)

**Goal**: Enable users to delete tasks with confirmation, task removed from list and database

**Spec Reference**: [User Story 7](spec.md#user-story-7---delete-task-priority-p2)

**Independent Test**: Task in list → click delete → confirmation dialog → confirm → task removed from list and database

**API Contract**: `DELETE /api/v1/tasks/{id}` (requires auth; response: 204 No Content)

### Implementation for User Story 7

#### Backend Tasks

- [ ] T111 [P] [US7] Create task deletion method in `backend/app/services/task_service.py`: delete_task(user_id, task_id)
- [ ] T112 [US7] Implement delete endpoint `DELETE /api/v1/tasks/{task_id}` in `backend/app/api/tasks.py`:
  - Require authentication
  - Verify user owns task
  - Delete task from database
  - Return 204 No Content on success
  - Error responses: 401 (unauthorized), 403 (not owner), 404 (not found)

#### Frontend Tasks

- [ ] T113 [P] [US7] Create task deletion service in `frontend/services/tasks.ts`: deleteTask function calling DELETE /api/v1/tasks/{id}
- [ ] T114 [US7] Add delete button to TaskItem component in `frontend/components/TaskItem.tsx`
- [ ] T115 [US7] Create confirmation dialog component in `frontend/components/ConfirmDialog.tsx`:
  - Modal overlay
  - Confirmation message: "Are you sure you want to delete this task?"
  - Cancel and Confirm buttons
  - Dismissible on background click or Esc key
- [ ] T116 [US7] Implement delete confirmation flow in `frontend/components/TaskItem.tsx`:
  - On delete button click: show confirmation dialog
  - On confirm: call deleteTask API
  - On success: remove task from TaskList, close dialog
  - On error: display error message, keep dialog
- [ ] T117 [P] [US7] Update TaskContext in `frontend/context/TaskContext.tsx`: add deleteTask action
- [ ] T118 [US7] Update useTasks hook in `frontend/hooks/useTasks.ts`: provide deleteTask action

#### Integration Tasks

- [ ] T119 [US7] Integration test: Task in list → click delete → confirmation dialog shows
- [ ] T120 [US7] Integration test: Delete confirmation → click confirm → task removed from list and database
- [ ] T121 [US7] Integration test: Delete confirmation → click cancel → task remains, dialog closes
- [ ] T122 [US7] Integration test: Delete task → refresh page → verify task no longer exists in database
- [ ] T123 [US7] Integration test: Dashboard with single task → delete task → empty state displays

**Checkpoint**: Task deletion fully functional. Users can delete tasks with confirmation, deleted tasks removed from UI and database immediately.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple stories, documentation, testing, and production readiness

**Duration**: ~2-3 hours

### Documentation & Deployment

- [ ] T124 [P] Update `README.md` at repository root with full setup, development, and deployment instructions
- [ ] T125 [P] Create/update `backend/README.md` with API documentation and cURL examples
- [ ] T126 [P] Create/update `frontend/README.md` with component structure and development guide
- [ ] T127 [P] Verify `specs/001-todo-app/quickstart.md` is accurate, update if needed

### Testing & Quality

- [ ] T128 [P] Run backend tests: `pytest backend/tests/` - ensure all pass
- [ ] T129 [P] Run frontend tests: `npm test` in frontend/ - ensure all pass
- [ ] T130 [P] Run linting and formatting: Python (black, flake8), JavaScript (eslint, prettier)
- [ ] T131 [P] Verify API contract: Test all endpoints in `contracts/openapi.yaml` work as specified
- [ ] T132 [P] End-to-end manual testing: Complete full user flow (register → login → add → edit → complete → delete → logout)

### Optimization & Hardening

- [ ] T133 [P] Verify environment variables not hardcoded anywhere, all secrets externalized
- [ ] T134 [P] Review database indexes: confirm on email, user_id, created_at per data-model.md
- [ ] T135 [P] Test error handling: database errors, validation errors, authentication failures all handled gracefully
- [ ] T136 [P] Verify responsive design on actual devices (mobile, tablet, desktop) or browser dev tools

### Pre-Production Checklist

- [ ] T137 Verify all user stories 1-4 work independently (MVP)
- [ ] T138 Verify all user stories 5-7 work (full feature)
- [ ] T139 Verify clean minimal design (no flashy colors, proper spacing, Notion-like)
- [ ] T140 Verify responsive on 320px (mobile), 768px (tablet), 1024px (desktop)
- [ ] T141 Test token expiry and refresh flow (if implemented)
- [ ] T142 Test database migration: `alembic upgrade head` succeeds

**Checkpoint**: Application fully tested, polished, and production-ready. All user stories functional, design clean and minimal, responsive across devices.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Setup (Phase 1)
    ↓
Foundational (Phase 2) ← BLOCKS ALL USER STORIES
    ↓
User Stories 1-4 (P1) ← MVP SCOPE
    ├─ US1: Registration (Phase 3)
    ├─ US2: Login (Phase 4)
    ├─ US3: View Dashboard (Phase 5)
    └─ US4: Add Tasks (Phase 6)
    ↓
User Stories 5-7 (P2) ← Additional Features
    ├─ US5: Mark Complete (Phase 7)
    ├─ US6: Update Task (Phase 8)
    └─ US7: Delete Task (Phase 9)
    ↓
Polish (Phase 10) ← Final touches
```

### Critical Path to MVP

**Minimum to ship**: Phases 1 → 2 → 3 → 4 → 5 → 6 → 10

**Time estimate**: ~2-3 weeks for experienced developer, ~4-5 weeks for team

### Within User Stories: Task Dependencies

**Models → Services → Endpoints → Frontend Integration**

- Models created first (T031, T032, etc.)
- Services depend on models (T032, T033, etc.)
- Endpoints depend on services (T044, T045, etc.)
- Frontend depends on working backend (T046 onwards)

### Parallelization Opportunities

**Phase 1 Setup** [P] tasks can run simultaneously:
- Backend structure (T001)
- Frontend structure (T002)
- Dependencies (T003, T004)
- Configuration (T005-T010)

**Phase 2 Foundational** [P] tasks within each section:
- Database models: T012, T013 parallel
- Middleware: T017, T018 parallel
- Frontend context/hooks: T021, T022, T023, T024, T025 parallel
- Testing setup: T029, T030 parallel

**Phase 3+ User Stories**: Can work on different stories in parallel
- Developer A: US1 (Registration)
- Developer B: US2 (Login)
- Developer C: US3 (Dashboard)
- Developer D: US4 (Add Tasks)

### Example: Parallel Execution (2 Developers)

**Day 1-2: Setup + Foundational (Both developers)**
- Run T001-T030 sequentially as blocking tasks

**Day 3-4: Frontend & Backend in Parallel**
- Dev A: Backend implementation (T031-T060) while
- Dev B: Frontend setup and components (T034-T068)

**Day 5-6: Integration**
- Both devs integrate and test together
- Debug any API/frontend mismatches

---

## Implementation Strategy

### MVP First (Recommended for First Deployment)

**Scope**: User Stories 1-4 (Registration, Login, View Tasks, Add Tasks)

**Steps**:
1. ✅ Phase 1: Setup (T001-T010)
2. ✅ Phase 2: Foundational (T011-T030) - CRITICAL
3. ✅ Phase 3: US1 Registration (T031-T042)
4. ✅ Phase 4: US2 Login (T043-T058)
5. ✅ Phase 5: US3 Dashboard (T059-T076)
6. ✅ Phase 6: US4 Add Tasks (T077-T087)
7. ✅ Phase 10: Polish (T124-T142)
8. **STOP and DEPLOY** - Ship MVP with 4 core features

**Timeline**: ~2 weeks for experienced developer

**Why MVP first**: Registration + login + view tasks + add tasks = fully functional todo app that delivers value immediately

### Incremental Delivery

**Deployment 1** (Week 2):
- Phases 1-6 (MVP: Register, Login, View, Add)

**Deployment 2** (Week 3):
- Phase 7 (Mark Complete)

**Deployment 3** (Week 3.5):
- Phase 8 (Update Task)

**Deployment 4** (Week 4):
- Phase 9 (Delete Task)

Each deployment adds value without breaking previous features.

---

## Notes & Best Practices

### Task Checklist

- [P] = Parallelizable (different files/modules, no blocking dependencies)
- [Story] = User story label (US1-US7) for traceability
- File paths = Exact location, specific to backend/ or frontend/ as appropriate

### Execution Guidelines

1. **Complete phases in order**: Setup → Foundational → Stories 1-4 (MVP) → Stories 5-7
2. **Test after each phase**: Run tests, manual verification, verify checkpoints
3. **Commit frequently**: After each task or logical group (e.g., after all models in Phase 2)
4. **Document as you go**: Comments in code, update README with new features
5. **Stop at checkpoints**: Validate independently testable increments

### Common Pitfalls to Avoid

- ❌ Skipping Phase 2 (Foundational) - will break all user stories
- ❌ Implementing frontend before backend API ready
- ❌ Not testing API contracts match openapi.yaml spec
- ❌ Hardcoding secrets (use environment variables)
- ❌ Ignoring responsive design until the end
- ❌ Forgetting to run tests before committing

### Success Criteria

- ✅ All tasks in Phase N complete and tested before moving to Phase N+1
- ✅ Each user story independently testable and deployable
- ✅ API responses match openapi.yaml exactly
- ✅ Database schema matches data-model.md exactly
- ✅ Frontend responsive on 320px-4K width
- ✅ No flashy colors, clean minimal design (Notion-like)
- ✅ All tests pass: pytest (backend) + npm test (frontend)
- ✅ Can complete full user flow without errors

---

## Summary

**Total Tasks**: 142 implementation tasks across 10 phases

**MVP Tasks** (Phases 1-6): 87 tasks → fully functional todo app with registration, login, dashboard, add tasks

**Additional Tasks** (Phases 7-9): 42 tasks → complete CRUD with mark complete, edit, delete

**Polish Tasks** (Phase 10): 13 tasks → documentation, testing, optimization, production readiness

**Parallelizable Tasks**: ~60 tasks marked [P] can run simultaneously within phases

**Estimated Time**:
- Solo developer: 3-4 weeks (sequential)
- Team of 2: 2-3 weeks (parallel after foundational)
- Team of 4: 1.5-2 weeks (full parallelization)

**Next Step**: Choose implementation strategy (MVP first recommended) and start Phase 1: Setup
