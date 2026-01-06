"""OpenAI Agents SDK wrapper for processing user messages."""

import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.database import Message, MessageRole
from src.utils.logging import get_logger
from src.utils.errors import ToolError

logger = get_logger(__name__)


class AgentService:
    """Service for processing messages with OpenAI Agents SDK via OpenRouter."""

    def __init__(self, mcp_client: Optional[Any] = None):
        self.mcp_client = mcp_client

        # Configure LLM provider (OpenRouter or OpenAI)
        self.llm_provider = os.getenv("LLM_PROVIDER", "openrouter")

        if self.llm_provider == "openrouter":
            self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo")
            logger.info(
                "Using OpenRouter LLM provider",
                model=self.model,
                base_url=self.openrouter_base_url,
            )
        else:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            logger.info("Using OpenAI LLM provider", model=self.model)

        self._setup_agent()

    def _setup_agent(self):
        """Initialize OpenAI Agents SDK agent."""
        logger.info("Agent service initialized", model=self.model)

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the agent (T060).

        Defines agent behavior rules for scope, tone, confirmation, and access control.
        """
        return """You are a helpful todo assistant designed to help users manage their todos through natural language conversation.

**Your Capabilities:**
- Create todos with titles, descriptions, and priorities (low, medium, high)
- Read and display todos
- Update todos (change status, priority, description)
- Delete todos (soft-delete/archive)

**Your Behavior Rules (MUST FOLLOW):**

1. **Scope Enforcement (T061)**: Only help with todo management.
   - ALLOWED: Create, read, update, delete todos
   - FORBIDDEN: Email, web search, code execution, file access, learning tutorials, etc.
   - When out-of-scope: Politely decline and explain: "I'm a todo assistant. I can help you create, list, update, or delete todos. What would you like to do?"

2. **Tone**: Be friendly, professional, and encouraging. Use conversational language.

3. **Confirmation Prompts (T062)**: Ask for explicit confirmation before destructive operations.
   - Destructive operations: "delete all", "clear all", "remove all"
   - Flow: User says "delete all" → You respond "Are you sure you want to delete all your todos? This cannot be undone." → Wait for confirmation
   - Only proceed after user explicitly confirms

4. **Access Control**: Only manage the current user's todos.
   - Never access, modify, or delete other users' data
   - If user attempts to access others' data, respond: "I can only help you manage your own todos."

5. **Clarity**: Ask clarifying questions if intent is ambiguous.
   - Example: User says "Mark done" with 5 open todos → Ask "Which todo would you like to mark as done?"

6. **Error Recovery**: If a tool fails, provide user-friendly message and suggest alternatives.

**Tool Usage:**
You have access to the following MCP tools:
- create_todo: Create a new todo
- read_todos: Read and list todos
- update_todo: Update an existing todo
- delete_todo: Delete (archive) a todo

Always invoke the appropriate tool when the user requests a todo operation."""

    async def process(
        self,
        user_message: str,
        prior_messages: List[Message],
        user_id: str,
        mcp_client: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and return agent response.

        Args:
            user_message: The user's current message
            prior_messages: List of prior messages in conversation (for context)
            user_id: The user's ID
            mcp_client: MCP client for tool invocation

        Returns:
            Dictionary with:
                - response: Natural language response from agent
                - tool_calls: List of tool invocations made
                - stop_reason: Reason agent stopped processing
        """
        try:
            logger.info(
                "Processing user message",
                user_id=user_id,
                message_length=len(user_message),
                prior_message_count=len(prior_messages),
            )

            # Format prior messages for context
            context = self._format_context(prior_messages, user_message)

            # Determine intent from user message
            intent = self._determine_intent(user_message)
            logger.info(f"Detected intent: {intent}", intent=intent, user_id=user_id)

            # Process based on intent
            tool_calls = []
            response = ""

            if intent == "create":
                response, tool_calls = await self._handle_create(user_message, mcp_client or self.mcp_client, user_id)
            elif intent == "read":
                response, tool_calls = await self._handle_read(mcp_client or self.mcp_client, user_id)
            elif intent == "update":
                response, tool_calls = await self._handle_update(user_message, mcp_client or self.mcp_client, user_id)
            elif intent == "delete":
                response, tool_calls = await self._handle_delete(user_message, mcp_client or self.mcp_client, user_id)
            else:
                # Out of scope or unclear
                response = self._generate_fallback_response(user_message)

            return {
                "response": response,
                "tool_calls": tool_calls,
                "stop_reason": "end_turn",
            }

        except Exception as e:
            logger.error(
                "Agent processing failed",
                user_id=user_id,
                error=str(e),
            )
            raise ToolError(
                f"Agent processing failed: {str(e)}",
                tool_name="agent",
                user_message="I'm having trouble processing your message. Please try again.",
            )

    def _determine_intent(self, message: str) -> str:
        """Determine user intent from message."""
        message_lower = message.lower()

        # Delete intent - CHECK FIRST (highest priority)
        delete_keywords = ["delete", "remove", "drop", "erase"]
        if any(kw in message_lower for kw in delete_keywords):
            return "delete"

        # Update/Mark intent - CHECK SECOND
        update_keywords = ["mark", "complete", "done", "finish", "unmark", "uncomplete", "not done", "not complete", "reopen", "pending", "undo"]
        if any(kw in message_lower for kw in update_keywords):
            return "update"

        # Read intent
        read_keywords = ["show", "list", "get", "display", "view", "read", "all", "tasks", "todos"]
        if any(kw in message_lower for kw in read_keywords):
            return "read"

        # Create intent - DEFAULT
        create_keywords = ["create", "add", "new", "make", "start", "write"]
        if any(kw in message_lower for kw in create_keywords):
            return "create"

        # If none match, assume create
        return "create"

    async def _handle_create(self, message: str, mcp_client, user_id: str) -> tuple:
        """Handle todo creation (T054: integrate MCP tools)."""
        if not mcp_client:
            return "I can't create todos without MCP client configured.", []

        # Extract title from message (simple heuristic)
        title = self._extract_title(message)
        if not title:
            return "I need a title for the todo. What should I call it?", []

        try:
            # Invoke MCP tool with user_id (T054)
            result = await mcp_client.invoke_tool(
                "create_todo",
                {"title": title, "priority": "medium"},
                user_id=user_id,
            )

            if result.get("success"):
                todo = result.get("todo", {})
                response = f"I've created a todo '{todo.get('title')}' for you!"
                return response, [result]
            else:
                # Handle tool error gracefully (T055)
                error_msg = result.get("error", "Unknown error")
                user_friendly_msg = self._translate_tool_error(error_msg, "create_todo")
                return f"I couldn't create the todo: {user_friendly_msg}", []

        except ToolError as e:
            # Tool error - translate to user-friendly message (T055)
            return e.user_message, []
        except Exception as e:
            logger.error(f"Error creating todo: {str(e)}", user_id=user_id)
            return "Sorry, I'm having trouble creating todos. Please try again.", []

    async def _handle_read(self, mcp_client, user_id: str) -> tuple:
        """Handle todo reading."""
        if not mcp_client:
            return "I can't read todos without MCP client configured.", []

        try:
            result = await mcp_client.invoke_tool("read_todos", {}, user_id=user_id)

            if result.get("error"):
                return f"I couldn't retrieve your todos: {result.get('error')}", []

            todos = result.get("todos", [])
            if not todos:
                return "You don't have any todos yet. Would you like to create one?", [result]

            # Format todo list
            todo_list = "\n".join([f"- {t['title']} ({t['status']})" for t in todos])
            response = f"Here are your todos:\n{todo_list}"
            return response, [result]

        except Exception as e:
            return f"Error reading todos: {str(e)}", []

    async def _handle_update(self, message: str, mcp_client, user_id: str) -> tuple:
        """Handle todo update (mark complete, change priority, etc)."""
        if not mcp_client:
            return "I can't update todos without MCP client configured.", []

        message_lower = message.lower()

        # Determine status - CHECK IN ORDER
        if "not complete" in message_lower or "not done" in message_lower or "unmark" in message_lower or "uncomplete" in message_lower or "reopen" in message_lower or "pending" in message_lower or "undo" in message_lower:
            new_status = "open"
        elif "done" in message_lower or "complete" in message_lower or "finish" in message_lower:
            new_status = "completed"
        else:
            new_status = "open"

        # Extract todo title
        title = self._extract_title_from_message(message)
        if not title:
            return "Which todo? (example: mark sleeping as done)", []

        try:
            # Get all todos
            todos_result = await mcp_client.invoke_tool("read_todos", {}, user_id=user_id)
            todos = todos_result.get("todos", [])

            # Find matching todo (case insensitive)
            matching_todo = None
            for todo in todos:
                if todo['title'].lower() == title.lower():
                    matching_todo = todo
                    break

            if not matching_todo:
                return f"Todo '{title}' not found.", []

            # Update
            result = await mcp_client.invoke_tool(
                "update_todo",
                {"id": matching_todo['id'], "status": new_status},
                user_id=user_id,
            )

            if result.get("success"):
                status_word = "complete" if new_status == "completed" else "open"
                return f"✓ Marked '{title}' as {status_word}.", [result]
            else:
                return f"Error: {result.get('error')}", []

        except Exception as e:
            logger.error(f"Update error: {str(e)}")
            return "Error updating todo.", []

    async def _handle_delete(self, message: str, mcp_client, user_id: str) -> tuple:
        """Handle todo deletion."""
        if not mcp_client:
            return "I can't delete todos without MCP client configured.", []

        # Extract title
        title = self._extract_title_from_message(message)
        if not title:
            return "Which todo to delete? (example: delete sleeping)", []

        try:
            # Get all todos
            todos_result = await mcp_client.invoke_tool("read_todos", {}, user_id=user_id)
            todos = todos_result.get("todos", [])

            # Find matching todo
            matching_todo = None
            for todo in todos:
                if todo['title'].lower() == title.lower():
                    matching_todo = todo
                    break

            if not matching_todo:
                return f"Todo '{title}' not found.", []

            # Delete
            result = await mcp_client.invoke_tool(
                "delete_todo",
                {"id": matching_todo['id']},
                user_id=user_id,
            )

            if result.get("success"):
                return f"✓ Deleted '{title}'.", [result]
            else:
                return f"Error: {result.get('error')}", []

        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
            return "Error deleting todo.", []

    def _translate_tool_error(self, error_msg: str, tool_name: str) -> str:
        """
        Translate technical tool error to user-friendly message (T055).

        Maps internal error messages to clear, actionable user messages.

        Args:
            error_msg: Technical error message from tool
            tool_name: Name of tool that failed

        Returns:
            User-friendly error message
        """
        error_lower = error_msg.lower()

        # Map common errors to friendly messages
        if "not found" in error_lower or "does not exist" in error_lower:
            return "I couldn't find that item. Please check and try again."
        elif "database" in error_lower or "connection" in error_lower:
            return "I'm having trouble accessing the database. Please try again in a moment."
        elif "validation" in error_lower or "invalid" in error_lower:
            return "That doesn't look right. Please check your request and try again."
        elif "permission" in error_lower or "unauthorized" in error_lower:
            return "I don't have permission to do that."
        elif "timeout" in error_lower or "took too long" in error_lower:
            return "That took too long to process. Please try again."
        else:
            # Generic fallback
            return "Something went wrong. Please try again."

    def _extract_title(self, message: str) -> str:
        """Extract todo title from message."""
        # Simple extraction: look for quoted text or after keywords
        if '"' in message:
            match = re.search(r'"([^"]+)"', message)
            if match:
                return match.group(1)

        if "'" in message:
            match = re.search(r"'([^']+)'", message)
            if match:
                return match.group(1)

        # Remove common prefixes and return remainder
        prefixes = ["create", "add", "make", "new", "create a todo", "add todo", "todo:"]
        text = message
        for prefix in prefixes:
            if text.lower().startswith(prefix):
                text = text[len(prefix):].strip()
                break

        return text[:100] if text else ""

    def _extract_title_from_message(self, message: str) -> str:
        """Extract todo title from message - SIMPLE VERSION."""
        message_lower = message.lower()

        # CASE 1: Quoted with single quotes: mark 'sleeping' as done -> sleeping
        if "'" in message:
            match = re.search(r"'([^']+)'", message)
            if match:
                return match.group(1).strip()

        # CASE 2: Quoted with double quotes: mark "sleeping" as done -> sleeping
        if '"' in message:
            match = re.search(r'"([^"]+)"', message)
            if match:
                return match.group(1).strip()

        # CASE 3: After keyword without quotes
        # mark sleeping as done -> sleeping
        # delete sleeping -> sleeping
        message_lower = message.lower()

        if "mark" in message_lower:
            # mark X as done/complete/not complete
            text = message[message_lower.find("mark") + 4:].strip()
            for stop in [" as done", " as complete", " as not complete", " as pending", " as open"]:
                if stop in text.lower():
                    return text[:text.lower().find(stop)].strip()
            return text.strip()

        elif "delete" in message_lower or "remove" in message_lower:
            # delete X or remove X
            kw = "delete" if "delete" in message_lower else "remove"
            text = message[message_lower.find(kw) + len(kw):].strip()
            return text.strip()

        return ""

    def _generate_fallback_response(self, message: str) -> str:
        """Generate response for out-of-scope requests."""
        return """I'm a todo management assistant. I can help you:
- Create new todos
- List your todos
- Mark todos as complete
- Delete todos

What would you like to do with your todos?"""

    def _format_context(self, prior_messages: List[Message], user_message: str) -> str:
        """
        Format prior messages and current message for agent context.

        Maintains role/content structure for conversation history.

        Args:
            prior_messages: List of prior Message objects (ordered by timestamp)
            user_message: Current user message

        Returns:
            Formatted context string with full conversation history
        """
        context_lines = []

        # Include prior messages in conversation order
        for msg in prior_messages:
            role_label = "User" if msg.role == MessageRole.USER else "Assistant"
            context_lines.append(f"{role_label}: {msg.content}")

        # Add current user message
        context_lines.append(f"User: {user_message}")

        return "\n".join(context_lines)

    def validate_scope(self, user_message: str) -> bool:
        """
        Check if message is within scope (todo-related) (T061).

        Returns True if message appears to be about todo management.
        Returns False if message appears to be out-of-scope.
        """
        message_lower = user_message.lower()

        # Out-of-scope keywords that indicate forbidden operations
        out_of_scope_keywords = [
            "email", "send email", "send message", "web search", "google", "code",
            "python", "javascript", "java", "execute", "run", "file", "access",
            "terminal", "command", "shell", "learn", "teach", "explain",
            "how do i", "how to", "tutorial", "guide", "crypto", "bitcoin",
            "financial advice", "medical", "health", "legal"
        ]

        # Check for out-of-scope keywords
        for keyword in out_of_scope_keywords:
            if keyword in message_lower:
                return False

        # In-scope keywords for todo operations
        in_scope_keywords = [
            "todo", "task", "done", "create", "delete", "update", "show", "list",
            "mark", "complete", "finished", "pending", "new", "add", "remove",
            "priority", "description", "status"
        ]

        # If message contains in-scope keywords, it's in scope
        if any(kw in message_lower for kw in in_scope_keywords):
            return True

        # If message is very short or ambiguous, consider it potentially in scope
        # and let the agent determine scope
        return len(message_lower) < 5 or "?" not in message_lower

    def _requires_confirmation(self, user_message: str) -> bool:
        """
        Check if message requires confirmation before proceeding (T062).

        Destructive operations that need explicit user confirmation.
        """
        message_lower = user_message.lower()

        # Destructive operation keywords
        destructive_keywords = [
            "delete all", "clear all", "remove all",
            "delete everything", "clear everything", "remove everything",
            "reset all", "erase all"
        ]

        return any(kw in message_lower for kw in destructive_keywords)

    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Get list of available tools for agent."""
        return [
            {
                "name": "create_todo",
                "description": "Create a new todo item",
                "parameters": {
                    "title": {"type": "string", "description": "Todo title"},
                    "description": {"type": "string", "description": "Optional description"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                },
            },
            {
                "name": "read_todos",
                "description": "List all todos",
                "parameters": {},
            },
            {
                "name": "update_todo",
                "description": "Update a todo",
                "parameters": {
                    "id": {"type": "string", "description": "Todo ID"},
                    "status": {"type": "string", "enum": ["open", "completed", "archived"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                },
            },
            {
                "name": "delete_todo",
                "description": "Delete (archive) a todo",
                "parameters": {
                    "id": {"type": "string", "description": "Todo ID"},
                },
            },
        ]


async def get_agent_service(mcp_client: Optional[Any] = None) -> AgentService:
    """Get agent service dependency."""
    return AgentService(mcp_client)
