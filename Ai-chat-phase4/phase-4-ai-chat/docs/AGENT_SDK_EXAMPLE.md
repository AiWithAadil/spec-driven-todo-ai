# OpenAI Agents SDK Integration with OpenRouter

This document shows how to integrate the OpenAI Agents SDK with OpenRouter for the agent service.

## Installation

```bash
pip install openai
```

## Basic Example

### 1. Simple Agent with Tools

```python
import asyncio
import os
from openai import AsyncOpenAI

# Configure OpenRouter
client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
)

# Define tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_todo",
            "description": "Create a new todo item",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Todo title"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority level"
                    }
                },
                "required": ["title"]
            }
        }
    }
]

# System prompt
system_prompt = """You are a helpful todo assistant.
You help users manage their todos through natural language conversation.
When users ask to create a todo, use the create_todo tool.
When users ask to view todos, list them.
Always be helpful and friendly."""

async def process_message(user_message: str, previous_messages: list):
    """Process a user message with the agent."""

    # Build messages
    messages = previous_messages + [
        {"role": "user", "content": user_message}
    ]

    # Call agent with tools
    response = await client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo"),
        messages=[
            {"role": "system", "content": system_prompt}
        ] + messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.7,
        max_tokens=1024
    )

    return response

# Example usage
async def main():
    messages = []

    # User: "Create a todo to buy groceries"
    response = await process_message("Create a todo to buy groceries", messages)

    # Check if tool was called
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            print(f"Tool: {tool_call.function.name}")
            print(f"Args: {tool_call.function.arguments}")
    else:
        print(f"Response: {response.choices[0].message.content}")

    # Add assistant response to messages
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    messages.append({"role": "user", "content": "Create a todo to buy groceries"})

asyncio.run(main())
```

## Integration with AgentService

### Current Implementation (Stateless)

The current `AgentService` uses intent-based routing (keyword detection) for MVP:

```python
# src/services/agent.py
class AgentService:
    def __init__(self, mcp_client: Optional[Any] = None):
        self.llm_provider = os.getenv("LLM_PROVIDER", "openrouter")
        if self.llm_provider == "openrouter":
            self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo")

    async def process(self, user_message: str, prior_messages: list, user_id: str, mcp_client):
        # Current: Intent detection
        intent = self._determine_intent(user_message)

        # Dispatch to handler based on intent
        if intent == "create":
            return await self._handle_create(...)
        elif intent == "read":
            return await self._handle_read(...)
        # ...
```

### Enhanced Version (Using OpenAI Agents SDK)

To fully integrate OpenAI Agents SDK with OpenRouter:

```python
from openai import AsyncOpenAI

class AgentService:
    def __init__(self, mcp_client: Optional[Any] = None):
        self.mcp_client = mcp_client
        self.llm_provider = os.getenv("LLM_PROVIDER", "openrouter")

        # Initialize OpenAI client with OpenRouter
        if self.llm_provider == "openrouter":
            self.client = AsyncOpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            )
            self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo")
        else:
            self.client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    async def process(self, user_message: str, prior_messages: list, user_id: str, mcp_client):
        """Process message using OpenAI Agents SDK with tool calling."""

        # Build messages
        messages = [{"role": msg.role.value, "content": msg.content} for msg in prior_messages]
        messages.append({"role": "user", "content": user_message})

        # Define tools from MCP server
        tools = self._get_tools()

        # Call agent
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()}
            ] + messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1024
        )

        # Process response
        assistant_message = response.choices[0].message
        tool_calls = []

        # Handle tool calls
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Invoke tool via MCP client
                result = await mcp_client.invoke_tool(tool_name, tool_args)
                tool_calls.append(result)

        return {
            "response": assistant_message.content or "I've processed your request.",
            "tool_calls": tool_calls,
            "stop_reason": "end_turn"
        }

    def _get_tools(self) -> list:
        """Get tool definitions for OpenAI Agents SDK format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_todo",
                    "description": "Create a new todo item",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Todo title"},
                            "description": {"type": "string", "description": "Optional description"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_todos",
                    "description": "List all todos for the user",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_todo",
                    "description": "Update an existing todo",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Todo ID"},
                            "title": {"type": "string"},
                            "status": {"type": "string", "enum": ["open", "completed", "archived"]},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                        },
                        "required": ["id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_todo",
                    "description": "Delete (archive) a todo",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Todo ID"}
                        },
                        "required": ["id"]
                    }
                }
            }
        ]
```

## Tool Calling Flow

### How OpenAI Agents SDK with MCP Tools Works

```
User Message
    ↓
Agent (OpenAI via OpenRouter) analyzes message
    ↓
Agent decides which tool to call (if any)
    ↓
Tool Call: {name: "create_todo", args: {title: "..."}}
    ↓
MCP Client invokes tool via MCP Server
    ↓
Tool Result: {success: true, todo: {...}}
    ↓
Agent incorporates result into response
    ↓
Response to User: "I've created a todo 'Buy groceries'..."
```

## Configuration for OpenRouter

### Environment Variables

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-your-key-here
LLM_PROVIDER=openrouter

# Optional
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4-turbo
```

### Model Selection

Different models for different needs:

```python
# Fast and free
OPENROUTER_MODEL=meta-llama/llama-2-7b-chat

# Better quality, fast
OPENROUTER_MODEL=meta-llama/llama-2-13b-chat

# Best quality at free tier
OPENROUTER_MODEL=mistralai/mistral-7b-instruct

# Most capable (small charge)
OPENROUTER_MODEL=openai/gpt-4-turbo
```

## Example: Full Chat Loop with Agent SDK

```python
async def chat_session():
    agent = AgentService(mcp_client)
    conversation = []

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Process with agent
        result = await agent.process(
            user_message=user_input,
            prior_messages=conversation,
            user_id="user123",
            mcp_client=mcp_client
        )

        print(f"Assistant: {result['response']}")

        # Add to conversation history
        conversation.append(Message(
            role=MessageRole.USER,
            content=user_input
        ))
        conversation.append(Message(
            role=MessageRole.ASSISTANT,
            content=result['response']
        ))
```

## Performance Tips

1. **Batch Requests**: If possible, batch multiple requests to reduce API calls
2. **Model Selection**: Use smaller models (Llama 2 7B) for faster responses
3. **Temperature**: Lower temperature (0.5) for more deterministic responses
4. **Max Tokens**: Set reasonable limits to reduce latency
5. **Timeout**: Set timeouts on OpenRouter API calls

## Error Handling

```python
try:
    response = await client.chat.completions.create(
        model=self.model,
        messages=messages,
        tools=tools,
        timeout=30.0  # 30 second timeout
    )
except Exception as e:
    logger.error(f"OpenRouter API error: {e}")
    # Fallback to simpler response
    return {
        "response": "I'm having trouble processing your request. Please try again.",
        "tool_calls": [],
        "stop_reason": "error"
    }
```

## Testing

Test agent with OpenRouter:

```bash
# Set environment variables
export OPENROUTER_API_KEY=sk-or-v1-your-key
export OPENROUTER_MODEL=openai/gpt-4-turbo

# Run agent tests
pytest tests/contract/test_mcp_tools.py -v

# Run full integration tests
pytest tests/integration/ -v
```

## References

- OpenRouter Docs: https://openrouter.ai/docs
- OpenAI SDK: https://github.com/openai/openai-python
- Tool Calling Guide: https://platform.openai.com/docs/guides/function-calling
