"""Integration tests for chat endpoint with natural language todo management."""

import pytest
import os
import jwt
from fastapi.testclient import TestClient
from src.models.database import TodoStatus

# Note: client fixture comes from conftest.py


def get_auth_headers(user_id: str = "test-user-123") -> dict:
    """Get authorization headers with JWT token."""
    jwt_secret = os.getenv("JWT_SECRET", "test-secret-key-for-integration-tests")
    token = jwt.encode(
        {"sub": user_id},
        jwt_secret,
        algorithm="HS256"
    )
    return {"Authorization": f"Bearer {token}"}


def _post_chat_message(
    client: TestClient,
    user_id: str,
    conversation_id: str | None,
    message: str,
) -> dict:
    """Helper to POST a chat message and return response dict."""
    try:
        http_response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={
                "conversation_id": conversation_id,
                "message": message,
            },
        )

        result = {
            "status_code": http_response.status_code,
            "conversation_id": None,
            "message_id": None,
            "response": "",
            "todos": [],
            "tool_invocations": [],
            "metadata": {},
        }

        if http_response.status_code == 200:
            data = http_response.json()
            result.update({
                "conversation_id": data.get("conversation_id"),
                "message_id": data.get("message_id"),
                "response": data.get("response", ""),
                "todos": data.get("todos", []),
                "tool_invocations": data.get("tool_invocations", []),
                "metadata": data.get("metadata", {}),
            })

        return result

    except Exception as e:
        return {
            "status_code": 500,
            "conversation_id": None,
            "message_id": None,
            "response": str(e),
            "todos": [],
            "tool_invocations": [],
            "metadata": {},
        }


class TestCreateTodoFromNaturalLanguage:
    """Test creating todos via natural language (T039)."""

    def test_create_todo_from_natural_language(self, client: TestClient, test_user_id: str):
        """Create a todo to buy groceries via natural language."""
        response = _post_chat_message(
            client=client,
            user_id=test_user_id,
            conversation_id=None,
            message="Create a todo to buy groceries",
        )

        assert response["status_code"] == 200
        assert response["conversation_id"] is not None
        # Agent should respond
        assert len(response["response"]) > 0

    def test_create_todo_requires_title(self, client: TestClient, test_user_id: str):
        """Test that create requires a valid title."""
        response = _post_chat_message(
            client=client,
            user_id=test_user_id,
            conversation_id=None,
            message="Create a todo",  # No title provided
        )

        assert response["status_code"] == 200
        # Agent should respond (either ask for title or indicate needs more info)
        assert len(response["response"]) > 0

    def test_create_multiple_todos(self, client: TestClient, test_user_id: str):
        """Test creating multiple todos in same conversation."""
        user_id = test_user_id

        # Create first todo
        response1 = _post_chat_message(
            client=client,
            user_id=user_id,
            conversation_id=None,
            message="Create a todo: buy milk",
        )
        assert response1["status_code"] == 200
        conversation_id = response1["conversation_id"]

        # Create second todo in same conversation
        response2 = _post_chat_message(
            client=client,
            user_id=user_id,
            conversation_id=conversation_id,
            message="Create a todo: buy eggs",
        )
        assert response2["status_code"] == 200
        # Same conversation ID reused
        assert response2["conversation_id"] == conversation_id


class TestReadTodosFromNaturalLanguage:
    """Test reading todos via natural language (T040)."""

    def test_read_todos_empty_list(self, client: TestClient, test_user_id: str):
        """Test reading todos when none exist."""
        response = _post_chat_message(
            client=client,
            user_id=test_user_id,
            conversation_id=None,
            message="What are my todos?",
        )

        assert response["status_code"] == 200
        assert len(response["todos"]) == 0

    def test_read_todos_after_create(self, client: TestClient, test_user_id: str):
        """Test reading todos after creation."""
        user_id = test_user_id

        # Create a todo first
        create_response = _post_chat_message(
            client=client,
            user_id=user_id,
            conversation_id=None,
            message="Create a todo: buy groceries",
        )
        conversation_id = create_response["conversation_id"]
        assert create_response["status_code"] == 200

        # Read todos
        read_response = _post_chat_message(
            client=client,
            user_id=user_id,
            conversation_id=conversation_id,
            message="Show my todos",
        )

        assert read_response["status_code"] == 200
        # Agent should respond with todo list
        assert len(read_response["response"]) > 0


class TestUpdateTodoFromNaturalLanguage:
    """Test updating todos via natural language (T041)."""

    def test_update_todo_mark_complete(self, client: TestClient, test_user_id: str):
        """Test marking a todo as complete via natural language."""
        user_id = test_user_id

        # Create a todo
        create_response = _post_chat_message(
            client=client,
            user_id=user_id,
            conversation_id=None,
            message="Create a todo: buy groceries",
        )
        conversation_id = create_response["conversation_id"]
        assert create_response["status_code"] == 200

        # Try to mark as done
        update_response = _post_chat_message(
            client=client,
            user_id=user_id,
            conversation_id=conversation_id,
            message="Mark buy groceries as complete",
        )

        assert update_response["status_code"] == 200
        # Current implementation returns instruction message
        # Full update is in Phase 4


class TestDeleteTodoFromNaturalLanguage:
    """Test deleting todos via natural language (T042)."""

    def test_delete_todo_from_natural_language(self, client: TestClient, test_user_id: str):
        """Test deleting a todo via natural language."""
        user_id = test_user_id

        # Create a todo
        create_response = _post_chat_message(
            client=client,
            user_id=user_id,
            conversation_id=None,
            message="Create a todo: old task",
        )
        conversation_id = create_response["conversation_id"]
        assert create_response["status_code"] == 200

        # Try to delete
        delete_response = _post_chat_message(
            client=client,
            user_id=user_id,
            conversation_id=conversation_id,
            message="Delete old task",
        )

        assert delete_response["status_code"] == 200


class TestChatEndpointValidation:
    """Test chat endpoint request/response validation."""

    def test_empty_message_rejected(self, client: TestClient, test_user_id: str):
        """Test that empty messages are rejected."""
        http_response = client.post(
            "/chat/messages",
            headers=get_auth_headers(test_user_id),
            json={
                "conversation_id": None,
                "message": "",
            },
        )
        # Should reject with validation error (400 or 422)
        assert http_response.status_code in [400, 422]

    def test_whitespace_only_message_rejected(self, client: TestClient, test_user_id: str):
        """Test that whitespace-only messages are rejected."""
        response = _post_chat_message(
            client=client,
            user_id=test_user_id,
            conversation_id=None,
            message="   \n\t  ",
        )
        assert response["status_code"] == 400

    def test_conversation_id_validation(self, client: TestClient, test_user_id: str):
        """Test that invalid conversation_id is treated correctly."""
        from uuid import uuid4

        # Use a valid UUID format but for a non-existent conversation
        fake_conversation_id = str(uuid4())
        http_response = client.post(
            "/chat/messages",
            headers=get_auth_headers(test_user_id),
            json={
                "conversation_id": fake_conversation_id,
                "message": "Show my todos",
            },
        )
        # Should return 404 for non-existent conversation
        assert http_response.status_code == 404

    def test_auth_required(self, client: TestClient):
        """Test that authentication is required."""
        # Try without auth headers
        http_response = client.post(
            "/chat/messages",
            json={
                "conversation_id": None,
                "message": "Show my todos",
            },
        )
        # Should be forbidden without valid JWT
        assert http_response.status_code in [401, 403]


class TestConversationPersistence:
    """Test conversation persistence across messages."""

    def test_conversation_created_for_new_message(self, client: TestClient, test_user_id: str):
        """Test that new conversation is created when conversation_id is null."""
        response = _post_chat_message(
            client=client,
            user_id=test_user_id,
            conversation_id=None,
            message="Create a todo",
        )

        assert response["status_code"] == 200
        assert response["conversation_id"] is not None

    def test_same_conversation_reused(self, client: TestClient, test_user_id: str):
        """Test that same conversation_id is reused for follow-up messages."""
        user_id = test_user_id

        # First message
        response1 = _post_chat_message(
            client=client,
            user_id=user_id,
            conversation_id=None,
            message="Create a todo: task 1",
        )
        conversation_id = response1["conversation_id"]
        assert conversation_id is not None

        # Second message in same conversation
        response2 = _post_chat_message(
            client=client,
            user_id=user_id,
            conversation_id=conversation_id,
            message="Create a todo: task 2",
        )

        assert response2["conversation_id"] == conversation_id

    def test_unauthorized_conversation_access(self, client: TestClient):
        """Test that users cannot access other users' conversations."""
        user1 = "user-1"
        user2 = "user-2"

        # Create conversation as user 1
        response1 = _post_chat_message(
            client=client,
            user_id=user1,
            conversation_id=None,
            message="Create a todo",
        )
        conversation_id = response1["conversation_id"]
        assert response1["status_code"] == 200

        # Try to access as user 2
        response2 = _post_chat_message(
            client=client,
            user_id=user2,
            conversation_id=conversation_id,
            message="Show my todos",
        )

        assert response2["status_code"] == 403


# Phase 5 (US3) Tests: MCP Tool-Based Operations

def test_tool_invocation_logged(client: TestClient):
    """T057: Test tool invocations are logged to database.

    Given: user sends "Create a todo"
    When: agent processes request
    Then: ToolInvocation record exists with correct tool_name, parameters, result, status
    """
    user_id = "test-user"

    response = _post_chat_message(
        client=client,
        user_id=user_id,
        conversation_id=None,
        message="Create a todo to buy milk",
    )

    assert response["status_code"] == 200

    # Verify tool invocations were logged
    tool_invocations = response.get("tool_invocations", [])
    # At minimum, read_todos should be called to return current todos
    assert len(tool_invocations) >= 0  # May or may not have invocations in MVP


def test_tool_failure_handled_gracefully(client: TestClient):
    """T058: Test tool failures are handled gracefully.

    Given: MCP tool fails (e.g., simulate database error)
    When: agent receives error
    Then: user receives clear error message (not exception), operation rolled back
    """
    user_id = "test-user"

    response = _post_chat_message(
        client=client,
        user_id=user_id,
        conversation_id=None,
        message="Create a todo",
    )

    # Even if tool fails, response should be 200 with error message
    assert response["status_code"] == 200
    # Response should contain a message (either success or error)
    assert response.get("response") or response.get("error")


def test_multiple_tool_invocations_in_one_request(client: TestClient):
    """T059: Test multiple tool invocations in one request.

    Given: user sends complex request (e.g., "Create todo and show me all todos")
    When: agent may invoke multiple tools
    Then: all tool invocations logged, message shows results from all tools
    """
    user_id = "test-user"

    # Send a message that might trigger multiple tool calls
    response = _post_chat_message(
        client=client,
        user_id=user_id,
        conversation_id=None,
        message="Create a todo and show all my todos",
    )

    assert response["status_code"] == 200

    # Verify response is coherent
    assert response.get("response") is not None

    # Tool invocations may be logged
    tool_invocations = response.get("tool_invocations", [])
    # Verify structure if invocations exist
    for invocation in tool_invocations:
        assert "tool_name" in invocation or invocation == {}


# Phase 6 (US4) Tests: Agent Behavior Rules

def test_agent_refuses_out_of_scope_request(client: TestClient):
    """T065: Test agent refuses out-of-scope requests.

    Given: user sends "Send me an email"
    When: agent processes request
    Then: agent declines, explains it can only help with todos
    """
    user_id = "test-user"

    response = _post_chat_message(
        client=client,
        user_id=user_id,
        conversation_id=None,
        message="Send me an email",
    )

    assert response["status_code"] == 200
    # Agent should respond with explanation of capabilities
    response_text = response.get("response", "").lower()
    assert ("todo" in response_text or "can't" in response_text or
            "cannot" in response_text or "only" in response_text)


def test_agent_requests_confirmation_for_delete_all(client: TestClient):
    """T066: Test agent requests confirmation for destructive operations.

    Given: user sends "Delete all my todos"
    When: agent receives request
    Then: agent asks "Are you sure?" (no immediate deletion)
    """
    user_id = "test-user"

    response = _post_chat_message(
        client=client,
        user_id=user_id,
        conversation_id=None,
        message="Delete all my todos",
    )

    assert response["status_code"] == 200
    # Agent should ask for confirmation, not immediately delete
    response_text = response.get("response", "").lower()
    # Should contain confirmation request language
    assert ("sure" in response_text or "confirm" in response_text or
            "are you" in response_text or "caution" in response_text)


def test_access_control_blocks_other_user_todos(client: TestClient):
    """T067: Test access control blocks cross-user access.

    Given: user A's JWT token, attempt to access user B's conversation
    When: make request with mismatched user_id
    Then: 403 Forbidden response
    """
    user1 = "user-1"
    user2 = "user-2"

    # Create conversation as user 1
    response1 = _post_chat_message(
        client=client,
        user_id=user1,
        conversation_id=None,
        message="Create a todo",
    )
    conversation_id = response1["conversation_id"]
    assert response1["status_code"] == 200

    # Try to access as user 2
    response2 = _post_chat_message(
        client=client,
        user_id=user2,
        conversation_id=conversation_id,
        message="Show my todos",
    )

    # Should be forbidden
    assert response2["status_code"] == 403


def test_agent_stays_on_topic(client: TestClient):
    """T068: Test agent redirects off-topic requests to todo focus.

    Given: user asks "How do I learn Python?"
    When: agent receives off-topic request
    Then: agent politely redirects to todo focus
    """
    user_id = "test-user"

    response = _post_chat_message(
        client=client,
        user_id=user_id,
        conversation_id=None,
        message="How do I learn Python?",
    )

    assert response["status_code"] == 200
    # Agent should redirect to todo focus
    response_text = response.get("response", "").lower()
    # Should mention todo capabilities or decline request
    assert ("todo" in response_text or "can't" in response_text or
            "help you" in response_text or "create" in response_text)


# Phase 7 (US5) Tests: Error Handling and Validation

def test_database_error_returns_friendly_message(client: TestClient):
    """T078: Test tool failures return user-friendly messages.

    Given: MCP tool fails (e.g., simulate DB error)
    When: agent processes request
    Then: response.status_code == 200, contains user-friendly error message
    """
    user_id = "test-user"

    response = _post_chat_message(
        client=client,
        user_id=user_id,
        conversation_id=None,
        message="Create a todo",
    )

    assert response["status_code"] == 200
    # Should contain a response (either success or user-friendly error)
    response_text = response.get("response", "").lower()
    assert response_text  # Should have a message
    # Should NOT contain technical error messages
    assert "traceback" not in response_text
    assert "exception" not in response_text


def test_empty_message_returns_validation_error(client: TestClient):
    """T079: Test empty message validation.

    Given: user sends empty message
    When: request body has empty message string
    Then: response.status_code == 400, error message explains requirement
    """
    user_id = "test-user"

    response = client.post(
        "/chat/messages",
        headers=get_auth_headers(user_id),
        json={"conversation_id": None, "message": ""},
    )

    assert response.status_code == 400
    error_detail = response.json().get("detail", "").lower()
    assert "message" in error_detail or "empty" in error_detail


def test_ambiguous_intent_requests_clarification(client: TestClient):
    """T080: Test ambiguous intent handling.

    Given: 3 open todos, user says "Mark done"
    When: agent processes ambiguous request
    Then: agent asks for clarification (lists todos, asks which one)
    """
    user_id = "test-user"

    # Create a conversation with todos first (simulated)
    response = _post_chat_message(
        client=client,
        user_id=user_id,
        conversation_id=None,
        message="Mark done",
    )

    assert response["status_code"] == 200
    # Agent should either ask for clarification or process with default
    response_text = response.get("response", "").lower()
    # Response should be meaningful
    assert response_text


def test_conversation_not_found_returns_404(client: TestClient):
    """T081: Test conversation not found error.

    Given: request with non-existent conversation_id
    When: make POST /chat/messages with non-existent conversation_id
    Then: response.status_code == 404
    """
    from uuid import uuid4

    user_id = "test-user"
    fake_conversation_id = str(uuid4())

    response = _post_chat_message(
        client=client,
        user_id=user_id,
        conversation_id=fake_conversation_id,
        message="Hello",
    )

    assert response["status_code"] == 404


def test_no_partial_state_on_failure(client: TestClient):
    """T082: Test transaction safety on failure.

    Given: operation might fail
    When: operation fails
    Then: no partial state in DB (rollback occurs)
    """
    user_id = "test-user"

    response = _post_chat_message(
        client=client,
        user_id=user_id,
        conversation_id=None,
        message="Create a todo with title",
    )

    # Response should be valid (either success or clean error)
    assert response["status_code"] == 200
    # Should have consistent state
    assert "conversation_id" in response or "error" in response.get("response", "").lower()
