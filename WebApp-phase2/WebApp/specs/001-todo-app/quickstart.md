# Phase 1: Quickstart & Local Development

**Date**: 2025-12-31
**Feature**: Web-based Todo Application

## Overview

This guide sets up the full stack locally for development:
- **PostgreSQL**: Database
- **FastAPI Backend**: Python async API server
- **Next.js Frontend**: React-based single-page app

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 14+ (or Docker)
- Git

---

## Option 1: Local Development (Manual)

### 1. Clone Repository

```bash
git clone <repository-url>
cd WebApp-phase2/WebApp
```

### 2. Set Up PostgreSQL Database

**Option A: Using Docker (Recommended)**

```bash
# Start PostgreSQL container
docker run --name todo-postgres \
  -e POSTGRES_PASSWORD=localpassword \
  -e POSTGRES_DB=todo_app \
  -p 5432:5432 \
  -d postgres:14
```

**Option B: Using Local PostgreSQL**

```bash
# Create database
createdb todo_app

# Verify connection
psql -d todo_app -c "SELECT 1;"
```

### 3. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with database URL:
# DATABASE_URL=postgresql://postgres:localpassword@localhost:5432/todo_app
# SECRET_KEY=your-super-secret-key-min-32-chars
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_HOURS=168

# Run migrations
alembic upgrade head

# Verify database schema
psql -d todo_app -c "\dt"

# Start development server
uvicorn app.main:app --reload --port 8000
```

**Backend should be running at**: `http://localhost:8000`
**API Documentation**: `http://localhost:8000/docs` (Swagger UI)

### 4. Set Up Frontend

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local
# Edit .env.local with:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Start development server
npm run dev
```

**Frontend should be running at**: `http://localhost:3000`

---

## Option 2: Docker Compose (All-in-One)

Create a `docker-compose.yml` in the project root (if not already present):

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    container_name: todo-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: localpassword
      POSTGRES_DB: todo_app
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: todo-backend
    environment:
      DATABASE_URL: postgresql://postgres:localpassword@postgres:5432/todo_app
      SECRET_KEY: your-super-secret-key-min-32-chars
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_HOURS: 168
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: todo-frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

**Run all services**:

```bash
docker-compose up
```

**Services**:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_auth_service.py

# Run integration tests
pytest tests/integration/
```

**Test Structure**:
```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests (services, models)
├── integration/          # Integration tests (API endpoints)
└── contract/            # Contract tests (API schema validation)
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- TaskForm.test.tsx
```

---

## Development Workflow

### 1. Database Changes

If you modify SQLAlchemy models:

```bash
cd backend

# Auto-generate migration
alembic revision --autogenerate -m "Add new field to task"

# Review the generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

### 2. API Changes

1. Update API endpoint in `backend/app/api/`
2. Update Pydantic schema in `backend/app/schemas.py`
3. Run backend tests to verify
4. Update OpenAPI spec (`specs/001-todo-app/contracts/openapi.yaml`) if contract changes
5. Update frontend service in `frontend/services/`

### 3. Frontend Changes

1. Update component in `frontend/components/`
2. Update page in `frontend/app/`
3. Update API service in `frontend/services/`
4. Run frontend tests to verify

---

## API Testing

### Using cURL

**Register**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Password123",
    "password_confirm": "Password123"
  }'
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Password123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2025-12-31T10:00:00Z"
  }
}
```

**List Tasks** (using token):
```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer eyJhbGci..."
```

**Create Task**:
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Update Task**:
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "is_completed": true
  }'
```

**Delete Task**:
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer eyJhbGci..."
```

### Using Swagger UI

Visit `http://localhost:8000/docs` for interactive API testing with auto-generated documentation.

---

## Environment Variables

### Backend (`backend/.env`)

```
DATABASE_URL=postgresql://postgres:localpassword@localhost:5432/todo_app
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=168
DEBUG=True
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Troubleshooting

### PostgreSQL Connection Error

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
```bash
# Verify PostgreSQL is running
psql -U postgres -c "SELECT 1;"

# Check environment variable
echo $DATABASE_URL

# Or verify Docker container
docker ps | grep postgres
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000 (backend) or 3000 (frontend)
lsof -i :8000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different ports
uvicorn app.main:app --port 8001  # Backend on 8001
npm run dev -- --port 3001         # Frontend on 3001
```

### CORS Errors

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**: Ensure backend CORS configuration includes frontend URL:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### JWT Token Expired

**Error**: `401 Unauthorized: Token expired`

**Solution**: Login again to get a new token. Token expires after 7 days (or custom `ACCESS_TOKEN_EXPIRE_HOURS`).

---

## Production Deployment Checklist

- [ ] Set strong `SECRET_KEY` in environment
- [ ] Use `DEBUG=False`
- [ ] Configure `CORS_ORIGINS` with production domain
- [ ] Set up managed PostgreSQL (AWS RDS, DigitalOcean, Railway)
- [ ] Use HTTPS (TLS certificate required)
- [ ] Set up environment variables securely (no .env in git)
- [ ] Run database migrations before deploying
- [ ] Build frontend for production: `npm run build`
- [ ] Set up monitoring and logging
- [ ] Configure backups for database
- [ ] Test authentication and token refresh flow

---

## Next Steps

1. **Run the app**: Start both backend and frontend
2. **Create user**: Register at `http://localhost:3000/auth/register`
3. **Login**: Login at `http://localhost:3000/auth/login`
4. **Add tasks**: Create and manage tasks on dashboard
5. **Run tests**: `pytest` (backend) and `npm test` (frontend)
6. **Review code**: Check generated API docs at `/docs`
7. **Iterate**: Make changes, tests pass, commit

---

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **JWT Introduction**: https://jwt.io/introduction
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## Quick Commands Reference

```bash
# Start everything with Docker Compose
docker-compose up

# Or manual setup:

# Terminal 1: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Test backend
cd backend && pytest -v

# Terminal 4: Test frontend
cd frontend && npm test
```
