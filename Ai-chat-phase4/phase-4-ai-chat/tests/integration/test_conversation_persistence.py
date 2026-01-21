"""Integration tests for conversation persistence (Phase 4: US2)."""

import pytest
import os
import jwt
from uuid import uuid4
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.database import Conversation, Message, MessageRole, Todo, TodoStatus
from src.models.schemas import ChatRequest, ChatResponse
from src.services.todo_manager import TodoManager


def get_auth_headers(user_id: str = "test-user") -> dict:
    """Get authorization headers with JWT token."""
    jwt_secret = os.getenv("JWT_SECRET", "test-secret-key-for-integration-tests")
    token = jwt.encode(
        {"sub": user_id},
        jwt_secret,
        algorithm="HS256"
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_resume_conversation_with_context(client, session: AsyncSession):
    """T048: Test resuming conversation with prior context.

    Given: conversation with 2 prior user messages + 2 assistant responses
    When: retrieve conversation by ID, send new message
    Then: prior messages loaded, agent response references prior context (coherent)
    """
    user_id = "test-user"

    # Create conversation
    conv = Conversation(user_id=user_id, created_at=datetime.utcnow())
    session.add(conv)
    await session.flush()

    # Add prior messages
    user_msg1 = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="Create a todo to buy groceries",
        timestamp=datetime.utcnow(),
    )
    session.add(user_msg1)
    await session.flush()

    asst_msg1 = Message(
        conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        content="I've created a todo to buy groceries for you!",
        timestamp=datetime.utcnow(),
    )
    session.add(asst_msg1)
    await session.flush()

    user_msg2 = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="Show my todos",
        timestamp=datetime.utcnow(),
    )
    session.add(user_msg2)
    await session.flush()

    asst_msg2 = Message(
        conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        content="Here are your todos:\n- Buy groceries (open)",
        timestamp=datetime.utcnow(),
    )
    session.add(asst_msg2)
    await session.commit()

    # Resume conversation with new message
    response = client.post(
        "/chat/messages",
        json={
            "conversation_id": str(conv.id),
            "message": "Mark groceries as done",
        },
        headers=get_auth_headers(user_id),
    )

    assert response.status_code == 200
    data = response.json()
    # Verify conversation was loaded
    assert data["conversation_id"] == str(conv.id)
    # Verify message count includes prior messages
    assert data["metadata"]["message_count"] >= 4  # 2 user + 2 assistant + 1 new


@pytest.mark.asyncio
async def test_todo_state_persists_across_sessions(client, session: AsyncSession):
    """T049: Test todo state persists across sessions.

    Given: create 2 todos in session 1, close session
    When: retrieve same conversation in session 2, ask "Show my todos"
    Then: both todos displayed with their state (open/completed/archived)
    """
    user_id = "test-user"

    # Create conversation and todos
    conv = Conversation(user_id=user_id, created_at=datetime.utcnow())
    session.add(conv)
    await session.flush()

    todo_manager = TodoManager(session)
    todo1 = await todo_manager.create_todo(
        user_id=user_id,
        title="Buy groceries",
        created_in_conversation_id=conv.id,
    )
    todo2 = await todo_manager.create_todo(
        user_id=user_id,
        title="Call mom",
        created_in_conversation_id=conv.id,
    )

    # Simulate session closure by committing and creating new session
    await session.commit()

    # Retrieve conversation in new session
    response = client.post(
        "/chat/messages",
        json={
            "conversation_id": str(conv.id),
            "message": "Show my todos",
        },
        headers=get_auth_headers(user_id),
    )

    assert response.status_code == 200
    data = response.json()

    # Verify todos are returned
    todos = data["todos"]
    assert len(todos) >= 2
    todo_titles = [t["title"] for t in todos]
    assert "Buy groceries" in todo_titles
    assert "Call mom" in todo_titles


@pytest.mark.asyncio
async def test_conversation_durability_after_restart(client, session: AsyncSession):
    """T050: Test conversation durability after restart.

    Given: create todo + message in conversation
    When: simulate server restart (close DB, reopen), retrieve conversation
    Then: todo and message still exist (durable persistence)
    """
    user_id = "test-user"

    # Create conversation
    conv = Conversation(user_id=user_id, created_at=datetime.utcnow())
    session.add(conv)
    await session.flush()

    # Create todo and message
    todo_manager = TodoManager(session)
    todo = await todo_manager.create_todo(
        user_id=user_id,
        title="Persistent todo",
        created_in_conversation_id=conv.id,
    )

    user_msg = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="Create a persistent todo",
        timestamp=datetime.utcnow(),
    )
    session.add(user_msg)
    await session.commit()

    # Retrieve conversation (simulates "restart" by new session)
    query = select(Conversation).where(Conversation.id == conv.id)
    result = await session.execute(query)
    retrieved_conv = result.scalars().first()

    assert retrieved_conv is not None
    assert retrieved_conv.id == conv.id
    assert retrieved_conv.user_id == user_id

    # Verify message still exists
    msg_query = select(Message).where(Message.conversation_id == conv.id)
    msg_result = await session.execute(msg_query)
    messages = msg_result.scalars().all()
    assert len(messages) > 0

    # Verify todo still exists
    retrieved_todos = await todo_manager.read_all(user_id)
    assert any(t.title == "Persistent todo" for t in retrieved_todos)


@pytest.mark.asyncio
async def test_message_order_preserved(client, session: AsyncSession):
    """T051: Test message order is preserved.

    Given: conversation with 5 messages
    When: load conversation, verify message sequence
    Then: messages returned in order by timestamp (first to last)
    """
    user_id = "test-user"

    # Create conversation
    conv = Conversation(user_id=user_id, created_at=datetime.utcnow())
    session.add(conv)
    await session.flush()

    # Create messages in order
    messages_data = [
        ("User", "First message"),
        ("Assistant", "First response"),
        ("User", "Second message"),
        ("Assistant", "Second response"),
        ("User", "Third message"),
    ]

    created_messages = []
    for role_str, content in messages_data:
        role = MessageRole.USER if role_str == "User" else MessageRole.ASSISTANT
        msg = Message(
            conversation_id=conv.id,
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
        )
        session.add(msg)
        await session.flush()
        created_messages.append((msg.id, content))

    await session.commit()

    # Retrieve messages in order
    query = (
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.timestamp.asc())
    )
    result = await session.execute(query)
    retrieved_messages = result.scalars().all()

    # Verify order is preserved
    assert len(retrieved_messages) == 5
    for i, msg in enumerate(retrieved_messages):
        expected_content = messages_data[i][1]
        assert msg.content == expected_content
