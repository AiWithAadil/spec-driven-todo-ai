"""MCP tool client for invoking tools."""

import json
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import ToolInvocation, Message, MessageRole
from src.utils.errors import ToolError
from src.utils.logging import get_logger

logger = get_logger(__name__)


class MCPClient:
    """Client for invoking MCP tools."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def invoke_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        message_id: Optional[UUID] = None,
        user_id: Optional[str] = None,
        timeout_seconds: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Invoke an MCP tool and log the invocation (T071, T074).

        Args:
            tool_name: Name of the tool to invoke
            parameters: Parameters for the tool
            message_id: Optional message ID for audit logging
            user_id: Optional user ID for context
            timeout_seconds: Timeout in seconds (default 5 seconds)

        Returns:
            Tool result dictionary with success/error fields

        Raises:
            ToolError: If tool invocation fails
        """
        import asyncio

        try:
            logger.info(
                f"Invoking MCP tool: {tool_name}",
                tool_name=tool_name,
                parameters=parameters,
                user_id=user_id,
            )

            # T074: Call tool with timeout
            try:
                result = await asyncio.wait_for(
                    self._execute_tool(tool_name, parameters, user_id=user_id),
                    timeout=timeout_seconds,
                )
            except asyncio.TimeoutError:
                # T074: Timeout - return user-friendly error
                logger.warning(
                    f"Tool invocation timeout: {tool_name}",
                    tool_name=tool_name,
                    timeout_seconds=timeout_seconds,
                )
                timeout_result = {
                    "success": False,
                    "error": f"Operation took too long (>{timeout_seconds}s)",
                    "user_message": "I'm taking longer than usual. Please try again.",
                }
                # Log the failure
                if message_id:
                    await self._log_invocation(
                        message_id=message_id,
                        tool_name=tool_name,
                        parameters=parameters,
                        result=timeout_result,
                        status="failure",
                    )
                return timeout_result

            # Validate result matches contract schema (T053)
            validated_result = await self._validate_tool_result(tool_name, result)

            # Log tool invocation if message_id provided (T052)
            if message_id:
                await self._log_invocation(
                    message_id=message_id,
                    tool_name=tool_name,
                    parameters=parameters,
                    result=validated_result,
                    status="success" if validated_result.get("success") else "failure",
                )

            logger.info(
                f"Tool {tool_name} executed successfully",
                tool_name=tool_name,
                success=validated_result.get("success"),
                message_id=str(message_id) if message_id else None,
            )

            return validated_result

        except ToolError:
            # Log tool failures
            if message_id:
                await self._log_invocation(
                    message_id=message_id,
                    tool_name=tool_name,
                    parameters=parameters,
                    result={"success": False, "error": "Tool execution failed"},
                    status="failure",
                )
            raise
        except Exception as e:
            logger.error(
                f"Tool invocation failed: {tool_name}",
                tool_name=tool_name,
                error=str(e),
                user_id=user_id,
            )
            raise ToolError(
                f"Failed to invoke {tool_name}: {str(e)}",
                tool_name=tool_name,
                user_message="I encountered an error while processing your request.",
                context={"error": str(e)},
            )

    async def _execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute the actual tool logic via MCP server."""
        if tool_name not in ["create_todo", "read_todos", "update_todo", "delete_todo"]:
            raise ToolError(
                f"Unknown tool: {tool_name}",
                tool_name=tool_name,
            )

        try:
            # Import here to avoid circular imports
            from src.mcp_server import get_mcp_server

            server = get_mcp_server()
            result = await server.handle_tool_call(
                tool_name=tool_name,
                parameters=parameters,
                user_id=user_id or "default-user",
            )
            return result

        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}", error=str(e))
            raise ToolError(
                f"Tool {tool_name} failed: {str(e)}",
                tool_name=tool_name,
            )

    async def _validate_tool_result(
        self, tool_name: str, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate tool result matches contract schema (T053).

        Ensures all results have required fields:
        - success: boolean
        - error: string or null
        - Additional fields depending on tool

        Args:
            tool_name: Name of tool that was invoked
            result: Result dictionary from tool

        Returns:
            Validated result dictionary

        Raises:
            ToolError: If result does not match contract
        """
        if not isinstance(result, dict):
            raise ToolError(
                f"Tool {tool_name} returned non-dict result: {type(result)}",
                tool_name=tool_name,
                user_message="Tool execution failed",
            )

        # Check required fields
        if "success" not in result:
            raise ToolError(
                f"Tool {tool_name} result missing 'success' field",
                tool_name=tool_name,
                user_message="Tool execution failed",
            )

        if "error" not in result:
            raise ToolError(
                f"Tool {tool_name} result missing 'error' field",
                tool_name=tool_name,
                user_message="Tool execution failed",
            )

        # Validate tool-specific schema
        if tool_name == "create_todo":
            if result.get("success") and "todo" not in result:
                raise ToolError(
                    f"Tool {tool_name} success result missing 'todo' field",
                    tool_name=tool_name,
                )
        elif tool_name == "read_todos":
            if "todos" not in result or "count" not in result:
                raise ToolError(
                    f"Tool {tool_name} result missing 'todos' or 'count' field",
                    tool_name=tool_name,
                )
        elif tool_name == "update_todo":
            if result.get("success") and "todo" not in result:
                raise ToolError(
                    f"Tool {tool_name} success result missing 'todo' field",
                    tool_name=tool_name,
                )
        elif tool_name == "delete_todo":
            if result.get("success") and "deleted_id" not in result:
                raise ToolError(
                    f"Tool {tool_name} success result missing 'deleted_id' field",
                    tool_name=tool_name,
                )

        logger.info(
            f"Tool {tool_name} result validated successfully",
            tool_name=tool_name,
            success=result.get("success"),
        )

        return result

    async def _log_invocation(
        self,
        message_id: UUID,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        status: str,
    ) -> None:
        """Log a tool invocation to the database."""
        try:
            # Verify message exists and is from assistant
            from sqlalchemy import select

            msg_query = select(Message).where(Message.id == message_id)
            msg_result = await self.session.execute(msg_query)
            message = msg_result.scalars().first()

            if not message:
                logger.warning(
                    "Message not found for tool invocation logging",
                    message_id=str(message_id),
                )
                return

            if message.role != MessageRole.ASSISTANT:
                logger.warning(
                    "Tool invocation logged for non-assistant message",
                    message_id=str(message_id),
                    role=message.role,
                )

            # Create ToolInvocation record
            invocation = ToolInvocation(
                message_id=message_id,
                tool_name=tool_name,
                parameters=json.dumps(parameters),
                result=json.dumps(result),
                status=status,
                timestamp=datetime.utcnow(),
            )

            self.session.add(invocation)
            await self.session.commit()

            logger.info(
                "Tool invocation logged",
                tool_name=tool_name,
                invocation_id=str(invocation.id),
            )

        except Exception as e:
            logger.error(
                "Failed to log tool invocation",
                tool_name=tool_name,
                message_id=str(message_id),
                error=str(e),
            )
            # Don't raise - logging failure shouldn't break the request


async def get_mcp_client(session: AsyncSession) -> MCPClient:
    """Get MCP client dependency."""
    return MCPClient(session)
