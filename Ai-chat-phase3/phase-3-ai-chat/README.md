# AI-Powered Todo Chatbot

A stateless REST API chatbot that manages todos through natural language conversation. Built with FastAPI, OpenAI Agents SDK, and PostgreSQL.

## Features

- **Natural Language Todo Management**: Create, read, update, and delete todos via conversation
- **Conversation Persistence**: Resume conversations across sessions with full context
- **MCP Tool Integration**: All operations executed through Model Context Protocol tools
- **Audit Logging**: Complete audit trail of all tool invocations
- **Error Handling**: Graceful error recovery with user-friendly messages

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL + SQLModel
- **AI**: OpenAI Agents SDK
- **Tools**: Model Context Protocol (MCP)
- **Testing**: pytest + pytest-asyncio

## Phase III Status

✅ **COMPLETE** - All Phase III requirements implemented:
- Backend API (FastAPI + OpenAI Agents SDK)
- MCP Tools (create_todo, read_todos, update_todo, delete_todo)
- Database persistence (Conversation, Message, Todo models)
- **Frontend UI (ChatKit-based - NEW!)**

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 12+ (or SQLite for local dev)
- OpenAI API key / OpenRouter API key
- Modern web browser

### Quick Start

1. **Backend**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   python -m uvicorn src.api.main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   python -m http.server 8080
   # Open http://localhost:8080
   ```

### Full Local Development

1. **Clone repository**:
   ```bash
   git clone <repo-url>
   cd phase-3-ai-chat
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   export $(cat .env | xargs)
   ```

5. **Initialize database**:
   ```bash
   python -c "
   import asyncio
   from src.db.connection import init_db
   asyncio.run(init_db())
   "
   ```

6. **Run application**:
   ```bash
   uvicorn src.api.main:app --reload
   ```

   Server will start at `http://localhost:8000`

### Docker Deployment

1. **Build and run**:
   ```bash
   cd docker
   docker-compose up --build
   ```

2. **Access application**:
   - API: `http://localhost:8000`
   - Docs: `http://localhost:8000/docs`

## API Usage

### Chat Endpoint

**POST** `/chat/messages`

Request:
```json
{
  "conversation_id": "uuid-or-null",
  "message": "Create a todo to buy groceries"
}
```

Response:
```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "response": "I've created a todo to buy groceries for you!",
  "todos": [
    {
      "id": "uuid",
      "title": "Buy groceries",
      "status": "open",
      "priority": "medium"
    }
  ],
  "tool_invocations": [...],
  "metadata": {
    "timestamp": "2026-01-02T10:01:00Z",
    "message_count": 1
  }
}
```

## Testing

### Run all tests:
```bash
pytest tests/ -v
```

### Run specific test suite:
```bash
pytest tests/unit/ -v          # Unit tests
pytest tests/contract/ -v      # Contract tests
pytest tests/integration/ -v   # Integration tests
```

### With coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Project Structure

```
.
├── src/
│   ├── api/              # FastAPI application
│   ├── services/         # Business logic
│   ├── models/           # Database and Pydantic schemas
│   ├── db/               # Database connection and migrations
│   └── utils/            # Utilities (logging, errors)
├── tests/                # Test suites
├── docker/               # Docker files
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Environment Variables

See `.env.example` for all available options:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key
- `JWT_SECRET`: Secret for JWT tokens
- `APP_ENV`: Environment (development/production)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

## Documentation

- **Specification**: `specs/001-ai-todo-chatbot/spec.md`
- **Architecture Plan**: `specs/001-ai-todo-chatbot/plan.md`
- **Data Model**: `specs/001-ai-todo-chatbot/data-model.md`
- **API Contracts**: `specs/001-ai-todo-chatbot/contracts/`

## Contributing

Follow the test-first (TDD) development cycle:
1. Write test (Red)
2. Implement code (Green)
3. Refactor for clarity (Refactor)

## License

Proprietary - Hackathon 2026
