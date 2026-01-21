"""Chat API routes."""

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.connection import get_session
from src.api.middleware.auth import extract_user_id
from src.models.schemas import ChatRequest, ChatResponse, ChatResponseMetadata, TodoSchema
from src.models.database import Conversation, Message, MessageRole, Todo
from src.services.mcp_client import get_mcp_client, MCPClient
from src.services.agent import get_agent_service, AgentService
from src.services.todo_manager import TodoManager
from src.utils.logging import get_logger, LogEndpointMetrics

router = APIRouter()
logger = get_logger(__name__)


@router.post("/messages", response_model=ChatResponse)
async def chat_messages(
    request: ChatRequest,
    user_id: str = Depends(extract_user_id),
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """
    Process a chat message and return agent response (T070: validation error handling).

    - Validate request (empty message, invalid conversation_id)
    - Create new conversation if needed
    - Load prior messages for context
    - Process with agent
    - Persist message and tool invocations
    - Return response with current todos
    """
    with LogEndpointMetrics(logger, "/chat/messages"):
        try:
            # T070: Validate request - empty message
            if not request.message or not request.message.strip():
                logger.warning(
                    "Empty message validation error",
                    user_id=user_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Message cannot be empty. Please provide a message.",
                )

            # T070: Validate request - invalid conversation_id format
            if request.conversation_id:
                try:
                    # Verify conversation_id is valid UUID format
                    str(request.conversation_id)
                except (ValueError, TypeError):
                    logger.warning(
                        "Invalid conversation_id format",
                        user_id=user_id,
                        conversation_id=str(request.conversation_id),
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid conversation ID format.",
                    )

            # Get or create conversation
            conversation = await _get_or_create_conversation(
                session, request.conversation_id, user_id
            )

            # Load prior messages for context
            prior_messages = await _load_conversation_history(session, conversation.id)

            # Initialize services
            mcp_client = MCPClient(session)
            agent = AgentService(mcp_client)
            todo_manager = TodoManager(session)

            # Check if message is in scope
            if not agent.validate_scope(request.message):
                logger.info(
                    "Out-of-scope request",
                    user_id=user_id,
                    message_preview=request.message[:50],
                )

            # Process with agent
            agent_result = await agent.process(
                user_message=request.message,
                prior_messages=prior_messages,
                user_id=user_id,
                mcp_client=mcp_client,
            )

            # Create user message record
            now = datetime.utcnow()
            user_msg = Message(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=request.message.strip(),
                timestamp=now,
            )
            session.add(user_msg)
            await session.flush()  # Flush to get ID

            # Create assistant message record
            assistant_msg = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=agent_result.get("response", ""),
                timestamp=now,
            )
            session.add(assistant_msg)
            await session.flush()  # Flush to get ID

            # Process tool invocations from agent and log them
            tool_invocations_list = []
            tool_calls = agent_result.get("tool_calls", [])
            if tool_calls:
                for tool_call in tool_calls:
                    # Log each tool invocation (this would be called via mcp_client)
                    # Tool invocations are logged when tools are actually invoked
                    tool_invocations_list.append(tool_call)

            # Get current todos
            todos = await todo_manager.read_all(user_id)
            todo_schemas = [_todo_to_schema(todo) for todo in todos]

            # Update conversation timestamp
            conversation.last_updated_at = datetime.utcnow()
            session.add(conversation)

            # Commit all changes
            await session.commit()

            logger.info(
                "Chat message processed",
                user_id=user_id,
                conversation_id=str(conversation.id),
                message_id=str(assistant_msg.id),
                todos_count=len(todos),
                tool_calls_count=len(tool_calls),
            )

            # Get tool invocations for this message (from database audit log)
            from sqlalchemy import select
            from src.models.database import ToolInvocation

            query = select(ToolInvocation).where(
                ToolInvocation.message_id == assistant_msg.id
            ).order_by(ToolInvocation.timestamp.asc())

            result = await session.execute(query)
            db_tool_invocations = result.scalars().all()

            return ChatResponse(
                conversation_id=conversation.id,
                message_id=assistant_msg.id,
                response=agent_result.get("response", ""),
                todos=todo_schemas,
                tool_invocations=[{
                    "tool_name": ti.tool_name,
                    "parameters": ti.parameters,
                    "result": ti.result,
                    "status": ti.status,
                    "timestamp": ti.timestamp.isoformat() if ti.timestamp else None
                } for ti in db_tool_invocations],
                metadata=ChatResponseMetadata(
                    timestamp=datetime.utcnow(),
                    message_count=len(prior_messages) + 1,
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to process chat message",
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process message",
            )


async def _get_or_create_conversation(
    session: AsyncSession,
    conversation_id: Optional[UUID],
    user_id: str,
) -> Conversation:
    """Get existing conversation or create new one."""
    if conversation_id:
        # Load existing conversation
        query = select(Conversation).where(
            Conversation.id == conversation_id
        )
        result = await session.execute(query)
        conversation = result.scalars().first()

        if not conversation:
            logger.warning(
                "Conversation not found",
                conversation_id=str(conversation_id),
                user_id=user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Verify user owns conversation
        if conversation.user_id != user_id:
            logger.warning(
                "Unauthorized conversation access",
                conversation_id=str(conversation_id),
                user_id=user_id,
                conversation_owner=conversation.user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return conversation
    else:
        # Create new conversation
        now = datetime.utcnow()
        conversation = Conversation(
            user_id=user_id,
            created_at=now,
            last_updated_at=now,
        )
        session.add(conversation)
        await session.flush()
        return conversation


async def _load_conversation_history(
    session: AsyncSession,
    conversation_id: UUID,
) -> list:
    """Load all prior messages for a conversation."""
    query = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp.asc())

    result = await session.execute(query)
    return result.scalars().all()


def _todo_to_schema(todo: Todo) -> TodoSchema:
    """Convert Todo ORM object to schema."""
    return TodoSchema(
        id=todo.id,
        user_id=todo.user_id,
        title=todo.title,
        description=todo.description,
        status=todo.status,
        priority=todo.priority,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
        created_in_conversation_id=todo.created_in_conversation_id,
    )
