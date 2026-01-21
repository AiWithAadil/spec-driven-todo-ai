# Quick Start: OpenRouter + AI Todo Chatbot

## 30-Second Setup

### 1. Your API Key is Ready ✓
```
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
```

### 2. Update `.env` file
The `.env` file already has your key configured. Verify it contains:
```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=openai/gpt-4-turbo
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Application
```bash
python -m uvicorn src.api.main:app --reload
```

### 5. Test the Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LXVzZXItMTIzIn0.test" \
  -d '{
    "conversation_id": null,
    "message": "Create a todo to buy groceries"
  }'
```

## Available Models

### Free (Fully Free)
```bash
# Ultra-fast
OPENROUTER_MODEL=meta-llama/llama-2-7b-chat

# Best quality free
OPENROUTER_MODEL=meta-llama/llama-2-13b-chat

# Strong performance
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
```

### Recommended (Small Charge)
```bash
# Best overall (recommended)
OPENROUTER_MODEL=openai/gpt-4-turbo

# GPT-3.5 (cheaper, still good)
OPENROUTER_MODEL=openai/gpt-3.5-turbo

# Claude 3 Haiku (good balance)
OPENROUTER_MODEL=anthropic/claude-3-haiku
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Only Contract Tests
```bash
pytest tests/contract/test_mcp_tools.py -v
```

### Expected Output
```
tests/contract/test_mcp_tools.py::TestCreateTodoContract::test_create_todo_success PASSED
tests/contract/test_mcp_tools.py::TestCreateTodoContract::test_create_todo_title_required PASSED
[... 14 more tests ...]
======================== 16 passed in 0.48s ========================
```

## API Endpoints

### Create Todo via Chat
```bash
curl -X POST http://localhost:8000/chat/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"conversation_id": null, "message": "Create a todo: buy milk"}'
```

### List Todos
```bash
curl -X POST http://localhost:8000/chat/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"conversation_id": null, "message": "Show my todos"}'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Monitoring Usage

1. Visit https://openrouter.ai/account/usage
2. Log in with your OpenRouter account
3. View real-time usage and costs
4. Check rate limits and quotas

## Common Issues

### Issue: "Invalid API Key"
**Solution**: Check your key in `.env` starts with `sk-or-v1-`

### Issue: "Model not found"
**Solution**: Use format `provider/model-name` (e.g., `openai/gpt-4-turbo`)

### Issue: "Rate limited"
**Solution**: Wait a moment and retry, or use a smaller model for faster responses

### Issue: "No response from agent"
**Solution**:
1. Check `.env` file is loaded: `echo $OPENROUTER_API_KEY`
2. Check logs: Look for "Using OpenRouter LLM provider"
3. Verify API key is valid at https://openrouter.ai

## Architecture Overview

```
User Request
    ↓
FastAPI Endpoint (/chat/messages)
    ↓
AgentService (detects intent)
    ↓
OpenAI Client (via OpenRouter)
    ↓
MCP Server (executes todo operations)
    ↓
TodoManager (database CRUD)
    ↓
PostgreSQL/SQLite
    ↓
Response to User
```

## Project Structure

```
phase-3-ai-chat/
├── .env                          # Your API keys (already configured)
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   └── routes/chat.py       # Chat endpoint
│   ├── services/
│   │   ├── agent.py             # Agent with OpenRouter support
│   │   ├── mcp_client.py        # MCP tool invoker
│   │   └── todo_manager.py      # Todo CRUD
│   ├── models/
│   │   ├── database.py          # SQLModel schemas
│   │   └── schemas.py           # Pydantic schemas
│   └── mcp_server.py            # MCP server (4 tools)
├── tests/
│   ├── contract/test_mcp_tools.py  # 16 passing tests
│   └── conftest.py              # Test fixtures
└── docs/
    ├── OPENROUTER_SETUP.md      # Detailed setup guide
    ├── AGENT_SDK_EXAMPLE.md     # Integration examples
    └── QUICKSTART_OPENROUTER.md # This file
```

## Next Steps

1. ✅ API key configured in `.env`
2. ✅ Dependencies installed
3. ✅ Tests passing (16/16)
4. ⏭️  Start the application: `uvicorn src.api.main:app --reload`
5. ⏭️  Test the endpoint with curl or Postman
6. ⏭️  Build integration tests

## Features Implemented

- ✅ **MCP Tools**: create_todo, read_todos, update_todo, delete_todo
- ✅ **Contract Tests**: All 16 tests passing
- ✅ **Agent Service**: Intent-based routing with OpenRouter support
- ✅ **Chat Endpoint**: Full stateless endpoint with database persistence
- ✅ **OpenRouter Support**: Configured and ready to use

## Getting Help

- OpenRouter Status: https://openrouter.ai/status
- OpenRouter Docs: https://openrouter.ai/docs
- Models Available: https://openrouter.ai/docs#models
- Rate Limits: https://openrouter.ai/docs#rate-limits

## Summary

You're all set! Your OpenRouter API key is:
- ✓ Integrated with the agent service
- ✓ Configured in `.env`
- ✓ Ready for use with OpenAI Agents SDK
- ✓ Supporting 4 MCP todo management tools
- ✓ Free tier for development

Run `uvicorn src.api.main:app --reload` and start testing the chat endpoint!
