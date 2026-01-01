# Phase 0: Research & Technology Decisions

**Date**: 2025-12-31
**Feature**: Web-based Todo Application
**Status**: Complete

## Technology Stack Decisions

### Backend Framework: FastAPI

**Decision**: Use FastAPI for HTTP API server

**Rationale**:
- Modern async-first design (handles concurrent users efficiently)
- Built-in OpenAPI/Swagger documentation
- Automatic request/response validation with Pydantic
- Excellent for RESTful APIs
- Easy JWT middleware integration
- Superior developer experience with type hints

**Alternatives Considered**:
- Django: More batteries-included but heavier, overkill for simple API
- Flask: More lightweight but lacks automatic validation and OpenAPI docs
- Node.js/Express: Would require JavaScript everywhere; Python chosen for backend simplicity

**Decision**: ✅ FastAPI selected

---

### Frontend Framework: Next.js 14+

**Decision**: Use Next.js with React and TypeScript

**Rationale**:
- App Router provides clean file-based routing (pages auto-map to routes)
- Server/Client component distinction for optimal performance
- Built-in API route support (though we'll use external backend)
- Zero-config deployment (Vercel or any Node.js host)
- Excellent TypeScript support
- Handles responsive design requirements natively
- Image optimization and code splitting built-in

**Alternatives Considered**:
- Create React App: Simpler setup but no routing, no SSR, no built-in optimizations
- Vue.js: Good framework but less ecosystem support for full-stack needs
- Svelte: Smaller bundle but smaller community/ecosystem

**Decision**: ✅ Next.js 14+ selected

---

### Database: PostgreSQL 14+

**Decision**: Use PostgreSQL for relational data storage

**Rationale**:
- ACID compliance guarantees data consistency
- Robust for multi-user scenarios (handles concurrent writes safely)
- Excellent support for migrations and schema versioning
- Wide hosting support (AWS RDS, DigitalOcean, Heroku, Railway, etc.)
- Strong JSON support if needed for flexible fields
- Free and open-source

**Alternatives Considered**:
- SQLite: Lacks concurrent write support, unsuitable for multi-user apps
- MongoDB: Overkill for simple relational data; adds complexity
- MySQL: Possible but PostgreSQL has better default semantics

**Decision**: ✅ PostgreSQL 14+ selected

---

### ORM: SQLAlchemy 2.0+

**Decision**: Use SQLAlchemy for Python-to-database mapping

**Rationale**:
- Declarative models make data structure clear and maintainable
- Automatic relationship management (User → Tasks)
- Built-in migration support via Alembic
- Type hints support in SQLAlchemy 2.0+
- Integrates seamlessly with FastAPI

**Alternatives Considered**:
- Raw SQL/asyncpg: More control but requires manual query writing
- Django ORM: Tied to Django; would need full Django setup
- Tortoise ORM: Async-first but smaller ecosystem

**Decision**: ✅ SQLAlchemy 2.0+ selected

---

### Authentication: JWT (JSON Web Tokens)

**Decision**: Use JWT for stateless authentication

**Rationale**:
- Stateless (no session storage needed on backend)
- Scales horizontally (can run multiple backend instances)
- Standard for REST APIs and SPAs
- Integrates easily with FastAPI
- Frontend stores token in localStorage or httpOnly cookie
- Clear spec-defined behavior (register → get token → authenticated requests)

**Alternatives Considered**:
- Session cookies: Requires server-side session storage; less scalable
- OAuth2/SSO: Overkill for internal todo app; adds third-party dependency
- Basic auth: Insecure without HTTPS (which is assumed)

**Decision**: ✅ JWT selected, token issued after successful login

---

### Frontend State Management: React Context API

**Decision**: Use React Context for auth and task state

**Rationale**:
- Built-in to React; no external library required
- Sufficient for simple auth state (user logged in/out) and task list
- Avoids complexity of Redux/MobX for MVP
- Easy to implement with custom hooks (useAuth, useTasks)
- Scales well for this application's scope (single feature)

**Alternatives Considered**:
- Redux: Overkill for a simple todo app; increases boilerplate
- Zustand: Lighter than Redux but still unnecessary complexity
- Prop drilling: Unmanageable without context/store

**Decision**: ✅ React Context with custom hooks selected

---

### Testing: pytest (Backend) + Jest/Vitest (Frontend)

**Decision**: Use pytest for backend, Jest/Vitest for frontend tests

**Rationale**:
- pytest: Industry standard for Python testing, excellent fixtures, easy async testing
- Jest/Vitest: Standard for JavaScript/React testing, good TypeScript support
- Follows spec requirement: test-first development
- Clear separation: unit, integration, contract tests

**Alternatives Considered**:
- unittest: Built-in Python but verbose, older syntax
- Mocha: Lighter JS test runner but Jest has better React integration

**Decision**: ✅ pytest + Jest/Vitest selected

---

## API Authentication Flow

**Overview**: JWT-based stateless authentication

**Registration Flow**:
```
POST /api/auth/register
  ├─ Payload: { email, password, passwordConfirm }
  ├─ Validation: email format, password match, no duplicate
  └─ Response: { accessToken, user: { id, email } }
```

**Login Flow**:
```
POST /api/auth/login
  ├─ Payload: { email, password }
  ├─ Validation: user exists, password correct
  └─ Response: { accessToken, user: { id, email } }
```

**Token Usage**:
```
GET /api/tasks
  ├─ Header: Authorization: Bearer <accessToken>
  ├─ Middleware: Verify token, extract user_id
  └─ Return: User's tasks
```

**Logout**: Client-side token deletion (frontend removes from localStorage)

**Token Details**:
- Expiration: 7 days (refresh token not implemented for MVP)
- Algorithm: HS256 (HMAC with SHA-256)
- Payload: `{ user_id, email, exp }`
- Secret: Environment variable (not hardcoded)

---

## Database Schema Overview

**User Table**:
- id (Primary Key)
- email (Unique, required)
- hashed_password (required)
- created_at (timestamp)

**Task Table**:
- id (Primary Key)
- user_id (Foreign Key → User)
- title (required, string)
- description (optional, text)
- is_completed (boolean, default False)
- created_at (timestamp)
- updated_at (timestamp)

**Relationships**:
- User has many Tasks (1:N)
- Task belongs to User

---

## API Route Summary

All routes prefixed with `/api/v1/` for versioning flexibility.

**Authentication Routes**:
- `POST /auth/register` → Create user account
- `POST /auth/login` → Authenticate and get token
- `POST /auth/logout` → Invalidate session (optional, client-side only)

**Task Routes** (all require Authorization header):
- `GET /tasks` → List all user's tasks
- `POST /tasks` → Create new task
- `GET /tasks/{id}` → Get single task details
- `PUT /tasks/{id}` → Update task (title, description, is_completed)
- `DELETE /tasks/{id}` → Delete task
- `PATCH /tasks/{id}` → Partial update (e.g., toggle completion)

---

## Deployment & Environment

**Development**:
- PostgreSQL: Local or Docker container
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`
- docker-compose.yml provided for local setup

**Production**:
- Database: Managed PostgreSQL (AWS RDS, DigitalOcean, Railway, Neon)
- Backend: Containerized (Docker) deployment (Railway, Heroku, DigitalOcean App Platform)
- Frontend: Static build deployment (Vercel, Netlify, S3+CloudFront)
- Environment variables: Externalized (no secrets in code)

---

## Constraints & Limitations

1. **No external APIs**: All functionality self-contained
2. **No real-time sync**: Polling or simple refresh; no WebSockets
3. **No file uploads**: Tasks are text-only
4. **Simple auth**: Email/password only, no MFA or OAuth
5. **Single database**: No sharding or replicas for MVP
6. **No caching**: Direct database queries; Redis optional future addition
7. **No background jobs**: No task queues; all operations synchronous

---

## Technology Stack Rationale Summary

| Component | Choice | Why Not Alternative |
|-----------|--------|---------------------|
| Backend | FastAPI | Flask too minimal, Django too heavy |
| Frontend | Next.js + React + TS | CRA too basic, Svelte too niche |
| Database | PostgreSQL | SQLite lacks concurrency, MongoDB too flexible |
| ORM | SQLAlchemy | Raw SQL too verbose, Tortoise too new |
| Auth | JWT | Sessions need storage, OAuth overkill |
| State | Context API | Redux/Zustand add complexity |
| Testing | pytest + Jest | unittest verbose, Mocha has less React support |

This stack is **production-ready, industry-standard, and scalable** while remaining **simple and focused** on the specification requirements.
