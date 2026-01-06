# OpenRouter Integration Guide

This document explains how to use OpenRouter as the LLM provider for the AI Todo Chatbot with the OpenAI Agents SDK.

## Why OpenRouter?

OpenRouter is a free, unified API gateway that provides access to multiple LLMs including:
- OpenAI models (GPT-4, GPT-4 Turbo, GPT-3.5)
- Anthropic models (Claude 3)
- Open source models (Llama 2, Mistral, etc.)
- Free tier with reasonable rate limits

Perfect for development and MVP testing without API costs.

## Setup

### 1. Get Your OpenRouter API Key

1. Visit https://openrouter.ai
2. Sign up (free account)
3. Go to Settings → API Keys
4. Copy your API key (starts with `sk-or-v1-`)

### 2. Configure Environment Variables

Create or update your `.env` file:

```bash
# LLM Configuration - Using OpenRouter (free tier)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-4-turbo
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Database Configuration
DATABASE_URL=sqlite:///./test.db

# JWT Configuration
JWT_SECRET=your-dev-secret-key-here

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
```

### 3. Available Models

Popular models available via OpenRouter:

**Free Tier Models:**
- `meta-llama/llama-2-7b-chat` - Fast, free
- `meta-llama/llama-2-13b-chat` - Better quality
- `mistralai/mistral-7b-instruct` - Strong performance
- `openai/gpt-3.5-turbo` - More capable

**Better Quality (small charge):**
- `openai/gpt-4-turbo` - Most capable, recommended
- `anthropic/claude-3-haiku` - Claude 3 Haiku
- `anthropic/claude-3-sonnet` - Claude 3 Sonnet

### 4. Model Selection

Edit `.env` to choose your model:

```bash
# For free tier (fully free):
OPENROUTER_MODEL=meta-llama/llama-2-13b-chat

# For best quality (small charge):
OPENROUTER_MODEL=openai/gpt-4-turbo

# For balance:
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
```

## Usage

The agent service automatically detects and uses OpenRouter when configured:

```python
# In src/services/agent.py
agent = AgentService(mcp_client)

# Agent will automatically use:
# - OpenRouter API key from OPENROUTER_API_KEY
# - Model from OPENROUTER_MODEL
# - Base URL from OPENROUTER_BASE_URL
```

## How It Works

### Agent Service Configuration

```python
if self.llm_provider == "openrouter":
    self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo")
```

### OpenAI SDK with OpenRouter

When using OpenAI Agents SDK, you can point it to OpenRouter:

```python
from openai import AsyncOpenAI

# Create client with OpenRouter endpoint
client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Use client with OpenAI SDK as normal
response = await client.chat.completions.create(
    model="openai/gpt-4-turbo",
    messages=[...],
)
```

## Rate Limits

OpenRouter's free tier includes:
- Reasonable rate limits per model
- Check https://openrouter.ai/docs#rate-limits for current limits
- Usually 10-20 requests per minute for free tier
- No daily limit, but cooling off if abused

## Cost (Optional Premium)

- Free tier: $0 (limited models, reasonable rate limits)
- Premium: Pay-as-you-go pricing per model
- View pricing at https://openrouter.ai/docs#pricing

## Testing

Run tests with OpenRouter configured:

```bash
# Load .env variables
export $(cat .env | xargs)

# Run agent service tests
python -m pytest tests/contract/ -v

# Start the application
uvicorn src.api.main:app --reload
```

## Fallback Configuration

If you want to support both OpenRouter and OpenAI:

```bash
# Primary: OpenRouter (free)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...

# Fallback: OpenAI (if OpenRouter not configured)
OPENAI_API_KEY=sk-...
```

The agent service will use OpenRouter if `LLM_PROVIDER=openrouter`, otherwise fall back to OpenAI.

## Troubleshooting

### API Key Invalid

- Check your API key starts with `sk-or-v1-`
- Verify it's correctly copied from OpenRouter settings
- Check `.env` file doesn't have extra spaces

### Model Not Found

- Verify model name matches OpenRouter format: `provider/model-name`
- Example: `openai/gpt-4-turbo`, `meta-llama/llama-2-13b-chat`
- List available models at https://openrouter.ai/docs#models

### Slow Responses

- Free tier models may be slower
- Check OpenRouter status page if service degraded
- Try a smaller/faster model (e.g., Llama 2 7B)

### Rate Limited

- Reduce request frequency
- Upgrade to premium tier
- Wait before retrying

## Best Practices

1. **Development**: Use free tier models for testing
2. **Production**: Use paid models for reliability (GPT-4 Turbo recommended)
3. **Cost Control**: Monitor usage at https://openrouter.ai/account/usage
4. **Fallback**: Keep `OPENAI_API_KEY` configured as backup
5. **Logging**: Check logs to verify OpenRouter is being used

## Environment Variables Reference

| Variable | Default | Example |
|----------|---------|---------|
| `LLM_PROVIDER` | `openrouter` | `openrouter` or `openai` |
| `OPENROUTER_API_KEY` | Required | `sk-or-v1-...` |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | Custom endpoint |
| `OPENROUTER_MODEL` | `openai/gpt-4-turbo` | `meta-llama/llama-2-13b-chat` |
| `OPENAI_API_KEY` | Optional fallback | `sk-...` |
| `OPENAI_MODEL` | `gpt-4o-mini` | Used if provider is `openai` |

## Next Steps

1. Add your OpenRouter API key to `.env`
2. Choose your preferred model
3. Run the application with OpenRouter configured
4. Test with `/chat/messages` endpoint
5. Monitor usage at https://openrouter.ai/account/usage

## Additional Resources

- OpenRouter Documentation: https://openrouter.ai/docs
- Available Models: https://openrouter.ai/docs#models
- Pricing: https://openrouter.ai/docs#pricing
- Status: https://openrouter.ai/status
