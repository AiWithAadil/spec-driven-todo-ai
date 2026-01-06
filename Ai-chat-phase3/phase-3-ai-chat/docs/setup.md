# Setup Guide (T088)

## Overview

This guide covers local development setup, Docker deployment, and troubleshooting for the AI-Powered Todo Chatbot.

## Prerequisites

- Python 3.9+
- SQLite3 (or PostgreSQL for production)
- Docker & Docker Compose (optional, for containerized setup)

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ai-todo-chatbot.git
cd ai-todo-chatbot
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example env file and update with your values:

```bash
cp .env.example .env
```

**Environment Variables**:

```env
# Database
DATABASE_URL=sqlite:///./chatbot.db

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

# LLM Provider (OpenRouter or OpenAI)
LLM_PROVIDER=openrouter  # or "openai"
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4-turbo

# Logging
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000
```

### 5. Initialize Database

```bash
# Create database tables
python -m src.db.connection
```

### 6. Run Application

```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Application will be available at `http://localhost:8000`

### 7. Test API

```bash
# Get a JWT token (for testing)
JWT_TOKEN=$(python -c "
import jwt
import os
payload = {'sub': 'test-user'}
token = jwt.encode(payload, 'your-secret-key-change-in-production', algorithm='HS256')
print(token)
")

# Call API
curl -X POST http://localhost:8000/chat/messages \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Docker Setup

### 1. Build Image

```bash
docker build -f docker/Dockerfile -t ai-todo-chatbot:latest .
```

### 2. Run Container

```bash
docker run -d \
  --name ai-todo-chatbot \
  -p 8000:8000 \
  -e JWT_SECRET=your-secret \
  -e OPENROUTER_API_KEY=your-key \
  ai-todo-chatbot:latest
```

### 3. Docker Compose (Recommended)

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

**Docker Compose Services**:
- `api`: FastAPI application (port 8000)
- `db`: SQLite database (volume mounted)

## Running Tests

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_todo_manager.py

# Run with coverage
pytest --cov=src tests/
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/

# Run specific integration test
pytest tests/integration/test_chat_endpoint.py::test_agent_refuses_out_of_scope_request

# Run smoke tests
pytest tests/integration/test_smoke.py -v

# Run performance tests
pytest tests/integration/test_performance.py -v
```

### Test Database

Integration tests use an in-memory SQLite database. No manual setup required.

## Common Issues

### Issue: "Module not found" errors

**Solution**: Ensure virtual environment is activated:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Issue: JWT token invalid

**Solution**: Ensure `JWT_SECRET` matches between token creation and verification:
```bash
# Token creation must use same secret as in .env
JWT_SECRET=your-secret-key-change-in-production
```

### Issue: Database locked (SQLite)

**Solution**: SQLite doesn't support concurrent writes well. For development:
- Close all running instances
- Use PostgreSQL for production

```bash
# Switch to PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db
```

### Issue: OpenRouter API key invalid

**Solution**: Verify your OpenRouter API key:
```bash
curl -X GET https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### Issue: Timeout errors (>5 seconds)

**Solution**: Check LLM provider latency. If consistently slow:
- Use faster model: `gpt-3.5-turbo` instead of `gpt-4`
- Check network connectivity
- Verify API key rate limits

### Issue: "Conversation not found" (404)

**Solution**: Conversation was not found. Common causes:
- Wrong conversation_id format
- Using conversation_id from different user
- Conversation expired (not stored)

Workaround: Omit `conversation_id` to start fresh conversation.

## Performance Tuning

### Database Optimization

For large todo lists (>1000 items):

1. **Use PostgreSQL instead of SQLite**
   ```bash
   DATABASE_URL=postgresql://user:pass@localhost/db
   ```

2. **Add database indexes** (auto-created via SQLAlchemy models)

3. **Test performance**
   ```bash
   pytest tests/integration/test_performance.py -v
   ```

### LLM Optimization

To improve response latency (<3 seconds target):

1. **Use faster model**:
   ```env
   OPENROUTER_MODEL=openai/gpt-3.5-turbo
   ```

2. **Reduce context length** (fewer prior messages)

3. **Enable response caching** (implement in future)

### API Optimization

1. **Enable compression** (built into FastAPI)

2. **Use connection pooling** (configured in `src/db/connection.py`)

3. **Monitor latency** (logged via `src/utils/logging.py`)

## Production Deployment

### Checklist

- [ ] Change `JWT_SECRET` to strong random value
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS/TLS
- [ ] Set `LOG_LEVEL=WARNING` to reduce log volume
- [ ] Use production LLM model (gpt-4, not gpt-3.5)
- [ ] Configure monitoring and alerting
- [ ] Set up database backups
- [ ] Run security scan: `bandit -r src/`
- [ ] Test error handling: `pytest tests/integration/test_chat_endpoint.py`

### Monitoring

Monitor these metrics via logs:

```json
{
  "timestamp": "2026-01-04T10:30:00Z",
  "level": "METRIC",
  "logger": "src.api.routes.chat",
  "message": "metric:endpoint_latency",
  "request_id": "abc-123",
  "endpoint": "/chat/messages",
  "latency_ms": 245.5,
  "status": "success",
  "status_code": 200
}
```

**Alert on**:
- latency_ms > 3000 (timeout approaching)
- status = "error" (any failed request)
- status_code >= 500 (server errors)

## Support

- API Documentation: `docs/api.md`
- MCP Tool Documentation: `docs/mcp-tools.md`
- Feature Specification: `specs/001-ai-todo-chatbot/spec.md`
- GitHub Issues: Report bugs and feature requests
