"""Smoke tests for API health and basic functionality (T089)."""

import pytest
import os
import jwt
from fastapi.testclient import TestClient


def get_auth_headers(user_id: str = "test-user") -> dict:
    """Get authorization headers with JWT token."""
    jwt_secret = os.getenv("JWT_SECRET", "test-secret-key-for-integration-tests")
    token = jwt.encode(
        {"sub": user_id},
        jwt_secret,
        algorithm="HS256"
    )
    return {"Authorization": f"Bearer {token}"}


class TestSmoke:
    """Smoke tests for basic endpoint health."""

    def test_health_check_chat_endpoint(self, client: TestClient):
        """T089: Test basic endpoint health.

        Given: API is running
        When: POST /chat/messages with simple message
        Then: response.status_code == 200, contains response and todos
        """
        user_id = "test-user"

        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={
                "conversation_id": None,
                "message": "Hello",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "conversation_id" in data
        assert "message_id" in data
        assert "response" in data
        assert "todos" in data
        assert "tool_invocations" in data
        assert "metadata" in data

        # Verify types
        assert isinstance(data["response"], str)
        assert isinstance(data["todos"], list)
        assert isinstance(data["tool_invocations"], list)

    def test_endpoint_returns_conversation_id(self, client: TestClient):
        """Test endpoint returns valid conversation ID."""
        user_id = "test-user"

        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Hello"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify conversation_id is UUID-like
        conversation_id = data["conversation_id"]
        assert conversation_id is not None
        assert isinstance(conversation_id, str)
        assert len(conversation_id) == 36  # UUID format
        assert conversation_id.count("-") == 4

    def test_endpoint_returns_message_id(self, client: TestClient):
        """Test endpoint returns valid message ID."""
        user_id = "test-user"

        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Hello"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify message_id is UUID-like
        message_id = data["message_id"]
        assert message_id is not None
        assert isinstance(message_id, str)
        assert len(message_id) == 36  # UUID format

    def test_endpoint_handles_auth_failure(self, client: TestClient):
        """Test endpoint rejects missing auth."""
        response = client.post(
            "/chat/messages",
            json={"message": "Hello"},
        )

        # Should be 401 or 403 (auth failure)
        assert response.status_code in [401, 403]

    def test_endpoint_handles_empty_message(self, client: TestClient):
        """Test endpoint rejects empty message."""
        user_id = "test-user"

        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": ""},
        )

        assert response.status_code == 400

    def test_multiple_requests_same_user(self, client: TestClient):
        """Test multiple requests work for same user."""
        user_id = "test-user"

        # First request
        response1 = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Hello"},
        )
        assert response1.status_code == 200

        # Second request
        response2 = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Hello again"},
        )
        assert response2.status_code == 200

        # Should have same or different conversation_id
        # (depends on whether agent created new conversation)
        assert response2.json()["conversation_id"] is not None

    def test_different_users_isolated(self, client: TestClient):
        """Test different users have isolated conversations."""
        user1 = "user-1"
        user2 = "user-2"

        # User 1 creates conversation
        response1 = client.post(
            "/chat/messages",
            headers=get_auth_headers(user1),
            json={"message": "Hello"},
        )
        assert response1.status_code == 200
        conversation_id = response1.json()["conversation_id"]

        # User 2 tries to access user 1's conversation
        response2 = client.post(
            "/chat/messages",
            headers=get_auth_headers(user2),
            json={
                "conversation_id": conversation_id,
                "message": "Hello",
            },
        )

        # Should be forbidden
        assert response2.status_code == 403

    def test_response_contains_agent_message(self, client: TestClient):
        """Test response contains agent's natural language message."""
        user_id = "test-user"

        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Hello"},
        )

        assert response.status_code == 200
        data = response.json()

        # Response should be non-empty string
        assert data["response"]
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    def test_metadata_contains_timestamp(self, client: TestClient):
        """Test response metadata contains timestamp."""
        user_id = "test-user"

        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Hello"},
        )

        assert response.status_code == 200
        data = response.json()

        # Metadata should have timestamp
        assert "metadata" in data
        assert "timestamp" in data["metadata"]
        assert isinstance(data["metadata"]["timestamp"], str)
        assert "T" in data["metadata"]["timestamp"]  # ISO format

    def test_all_fields_present(self, client: TestClient):
        """Test all expected response fields are present."""
        user_id = "test-user"

        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Create a todo"},
        )

        assert response.status_code == 200
        data = response.json()

        # All required fields
        required_fields = [
            "conversation_id",
            "message_id",
            "response",
            "todos",
            "tool_invocations",
            "metadata",
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"
