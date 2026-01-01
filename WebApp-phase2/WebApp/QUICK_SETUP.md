# Quick Setup - Todo App

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (or Docker)

## 5-Minute Setup

### 1. Database (Terminal 1)

**Option A: Docker**
```bash
docker run --name todo-postgres \
  -e POSTGRES_PASSWORD=localpassword \
  -e POSTGRES_DB=todo_app \
  -p 5432:5432 \
  -d postgres:14
```

**Option B: Local PostgreSQL**
```bash
createdb todo_app
```

### 2. Backend (Terminal 2)

```bash
cd backend

# Setup Python environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env          # Windows
cp .env.example .env            # macOS/Linux

# Run backend
uvicorn app.main:app --reload --port 8000
```

Backend ready at: **http://localhost:8000**

### 3. Frontend (Terminal 3)

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
copy .env.local.example .env.local    # Windows
cp .env.local.example .env.local      # macOS/Linux

# Run frontend
npm run dev
```

Frontend ready at: **http://localhost:3000**

## Test the App

1. Open http://localhost:3000
2. Click "Register" to create account
3. Enter email and password (min 8 chars)
4. After login, you'll see the dashboard
5. Add tasks, edit, complete, delete!

## Quick Commands

### Check if services running
```bash
# Backend health
curl http://localhost:8000/health

# Frontend
Open http://localhost:3000
```

### Stop all services
```bash
# Backend: Press Ctrl+C in Terminal 2
# Frontend: Press Ctrl+C in Terminal 3
# Database: docker stop todo-postgres
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database connection refused | Start PostgreSQL / Docker container |
| Port 8000 already in use | Change port: `uvicorn app.main:app --port 8001` |
| Port 3000 already in use | Use different port with `npm run dev -- -p 3001` |
| Module not found (Python) | Run: `pip install -r requirements.txt` |
| Module not found (Node) | Run: `npm install` |
| CORS errors | Ensure backend is running and CORS settings match |

## What Works Now

✅ Register with email/password
✅ Login with credentials
✅ View all tasks
✅ Add new tasks
✅ Edit task title/description
✅ Mark tasks complete
✅ Delete tasks
✅ Logout
✅ Responsive design

## Next Steps

- API Docs: http://localhost:8000/docs
- Run tests: `cd backend && pytest`
- Frontend tests: `cd frontend && npm test`

---

**Documentation**: See `STARTUP.md` for detailed setup and `IMPLEMENTATION_COMPLETE.md` for feature details.
