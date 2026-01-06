"""MCP Server implementation for todo tools."""

import json
import asyncio
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime
import sys

from src.db.connection import init_db, get_db_session
from src.services.todo_manager import TodoManager
from src.models.database import TodoStatus, TodoPriority
from src.utils.logging import get_logger

logger = get_logger(__name__)


class MCPServer:
    """MCP Server for todo management tools."""

    def __init__(self):
        """Initialize MCP server."""
        self.tools = self._define_tools()
        self.user_id = "default-user"  # Would be provided by agent context

    def _define_tools(self) -> Dict[str, Dict[str, Any]]:
        """Define available tools."""
        return {
            "create_todo": {
                "description": "Create a new todo item",
                "parameters": {
                    "title": {"type": "string", "description": "Todo title (required)"},
                    "description": {"type": "string", "description": "Todo description (optional)"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority level (default: medium)",
                    },
                },
            },
            "read_todos": {
                "description": "Read and list todos",
                "parameters": {
                    "conversation_id": {
                        "type": "string",
                        "description": "Optional conversation ID to filter todos",
                    },
                },
            },
            "update_todo": {
                "description": "Update an existing todo",
                "parameters": {
                    "id": {"type": "string", "description": "Todo ID (required)"},
                    "title": {"type": "string", "description": "New title (optional)"},
                    "description": {"type": "string", "description": "New description (optional)"},
                    "status": {
                        "type": "string",
                        "enum": ["open", "completed", "archived"],
                        "description": "New status (optional)",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "New priority (optional)",
                    },
                },
            },
            "delete_todo": {
                "description": "Delete (archive) a todo",
                "parameters": {
                    "id": {"type": "string", "description": "Todo ID (required)"},
                },
            },
        }

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get available tools."""
        return self.tools

    async def handle_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_id: str = "default-user",
    ) -> Dict[str, Any]:
        """
        Handle a tool call.

        Args:
            tool_name: Name of the tool to call
            parameters: Parameters for the tool
            user_id: User ID making the request

        Returns:
            Tool result dictionary
        """
        self.user_id = user_id
        logger.info(f"Handling tool call: {tool_name}", tool_name=tool_name, user_id=user_id)

        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
            }

        try:
            if tool_name == "create_todo":
                return await self.create_todo(parameters)
            elif tool_name == "read_todos":
                return await self.read_todos(parameters)
            elif tool_name == "update_todo":
                return await self.update_todo(parameters)
            elif tool_name == "delete_todo":
                return await self.delete_todo(parameters)
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}", error=str(e))
            return {
                "success": False,
                "error": str(e),
            }

    async def create_todo(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new todo."""
        try:
            # Validate required parameter
            title = parameters.get("title")
            if not title:
                return {
                    "success": False,
                    "todo": None,
                    "error": "Title is required and must be non-empty",
                }

            # Parse parameters
            description = parameters.get("description")
            priority_str = parameters.get("priority", "medium")

            # Validate priority
            try:
                priority = TodoPriority(priority_str)
            except ValueError:
                return {
                    "success": False,
                    "todo": None,
                    "error": f"Invalid priority value: {priority_str}",
                }

            # Create todo
            session = await get_db_session()
            try:
                manager = TodoManager(session)
                todo = await manager.create_todo(
                    user_id=self.user_id,
                    title=title,
                    description=description,
                    priority=priority,
                )

                return {
                    "success": True,
                    "todo": {
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status.value,
                        "priority": todo.priority.value,
                        "created_at": todo.created_at.isoformat() + "Z",
                    },
                    "error": None,
                }
            finally:
                await session.close()

        except Exception as e:
            return {
                "success": False,
                "todo": None,
                "error": f"Database error: {str(e)}",
            }

    async def read_todos(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Read todos for user."""
        try:
            session = await get_db_session()
            try:
                manager = TodoManager(session)
                todos = await manager.read_all(user_id=self.user_id)

                return {
                    "success": True,
                    "todos": [
                        {
                            "id": str(todo.id),
                            "title": todo.title,
                            "description": todo.description,
                            "status": todo.status.value,
                            "priority": todo.priority.value,
                            "created_at": todo.created_at.isoformat() + "Z",
                            "updated_at": todo.updated_at.isoformat() + "Z",
                        }
                        for todo in todos
                    ],
                    "count": len(todos),
                    "error": None,
                }
            finally:
                await session.close()

        except Exception as e:
            return {
                "success": False,
                "todos": [],
                "count": 0,
                "error": f"Database error: {str(e)}",
            }

    async def update_todo(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update a todo."""
        try:
            # Validate required parameter
            todo_id_str = parameters.get("id")
            if not todo_id_str:
                return {
                    "success": False,
                    "todo": None,
                    "error": "Todo ID is required",
                }

            # Parse UUID
            try:
                todo_id = UUID(todo_id_str)
            except ValueError:
                return {
                    "success": False,
                    "todo": None,
                    "error": f"Invalid id format: {todo_id_str}",
                }

            # Parse optional fields
            title = parameters.get("title")
            description = parameters.get("description")
            status_str = parameters.get("status")
            priority_str = parameters.get("priority")

            # Parse status if provided
            status = None
            if status_str:
                try:
                    status = TodoStatus(status_str)
                except ValueError:
                    return {
                        "success": False,
                        "todo": None,
                        "error": f"Invalid status value: {status_str}",
                    }

            # Parse priority if provided
            priority = None
            if priority_str:
                try:
                    priority = TodoPriority(priority_str)
                except ValueError:
                    return {
                        "success": False,
                        "todo": None,
                        "error": f"Invalid priority value: {priority_str}",
                    }

            # Update todo
            session = await get_db_session()
            try:
                manager = TodoManager(session)
                todo = await manager.update(
                    todo_id=todo_id,
                    user_id=self.user_id,
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                )

                if not todo:
                    return {
                        "success": False,
                        "todo": None,
                        "error": "Todo not found",
                    }

                return {
                    "success": True,
                    "todo": {
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status.value,
                        "priority": todo.priority.value,
                        "updated_at": todo.updated_at.isoformat() + "Z",
                    },
                    "error": None,
                }
            finally:
                await session.close()

        except Exception as e:
            return {
                "success": False,
                "todo": None,
                "error": f"Database error: {str(e)}",
            }

    async def delete_todo(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Delete (archive) a todo."""
        try:
            # Validate required parameter
            todo_id_str = parameters.get("id")
            if not todo_id_str:
                return {
                    "success": False,
                    "deleted_id": None,
                    "error": "Todo ID is required",
                }

            # Parse UUID
            try:
                todo_id = UUID(todo_id_str)
            except ValueError:
                return {
                    "success": False,
                    "deleted_id": None,
                    "error": f"Invalid id format: {todo_id_str}",
                }

            # Delete todo
            session = await get_db_session()
            try:
                manager = TodoManager(session)
                success = await manager.delete(todo_id, self.user_id)

                if not success:
                    return {
                        "success": False,
                        "deleted_id": None,
                        "error": "Todo not found",
                    }

                return {
                    "success": True,
                    "deleted_id": str(todo_id),
                    "error": None,
                }
            finally:
                await session.close()

        except Exception as e:
            return {
                "success": False,
                "deleted_id": None,
                "error": f"Database error: {str(e)}",
            }


# Global MCP server instance
_server = None


def get_mcp_server() -> MCPServer:
    """Get or create MCP server instance."""
    global _server
    if _server is None:
        _server = MCPServer()
    return _server


async def main():
    """Run MCP server."""
    await init_db()
    server = get_mcp_server()
    print(f"MCP Server started with {len(server.get_tools())} tools", file=sys.stderr)
    # Server is ready for tool invocations
    # In production, this would connect to MCP protocol
    return server


if __name__ == "__main__":
    asyncio.run(main())
