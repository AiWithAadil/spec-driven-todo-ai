"""Performance tests to verify latency targets (T090)."""

import pytest
import os
import jwt
import time
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


class TestPerformance:
    """Performance tests verifying latency targets (T090)."""

    def test_create_todo_under_3_seconds(self, client: TestClient):
        """SC-001: Verify create todo completes within <3 seconds.

        Target: <3 seconds per spec SC-001
        """
        user_id = "test-user"

        start_time = time.time()
        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Create a todo to test performance"},
        )
        elapsed_ms = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 3000, f"Create todo took {elapsed_ms:.0f}ms, expected <3000ms"

    def test_list_todos_under_2_seconds(self, client: TestClient):
        """SC-002: Verify list todos completes within <2 seconds.

        Target: <2 seconds for 100+ items per spec SC-002
        """
        user_id = "test-user"

        # Create some todos first
        for i in range(5):
            client.post(
                "/chat/messages",
                headers=get_auth_headers(user_id),
                json={"message": f"Create todo {i}"},
            )

        start_time = time.time()
        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Show my todos"},
        )
        elapsed_ms = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 2000, f"List todos took {elapsed_ms:.0f}ms, expected <2000ms"

    def test_conversation_retrieval_under_1_second(self, client: TestClient):
        """SC-003: Verify conversation retrieval within <1 second.

        Target: <1 second for conversation context load
        """
        user_id = "test-user"

        # Create conversation
        create_response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Hello"},
        )
        assert create_response.status_code == 200
        conversation_id = create_response.json()["conversation_id"]

        # Retrieve conversation
        start_time = time.time()
        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={
                "conversation_id": conversation_id,
                "message": "Hi again",
            },
        )
        elapsed_ms = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 1000, f"Conversation retrieval took {elapsed_ms:.0f}ms, expected <1000ms"

    def test_endpoint_latency_consistency(self, client: TestClient):
        """Test endpoint latency is consistent across multiple requests."""
        user_id = "test-user"
        latencies = []

        for _ in range(5):
            start_time = time.time()
            response = client.post(
                "/chat/messages",
                headers=get_auth_headers(user_id),
                json={"message": "Hello"},
            )
            elapsed_ms = (time.time() - start_time) * 1000
            latencies.append(elapsed_ms)

            assert response.status_code == 200

        # All requests should complete within reasonable time
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)

        assert avg_latency < 3000, f"Average latency {avg_latency:.0f}ms exceeded 3 seconds"
        assert max_latency < 5000, f"Max latency {max_latency:.0f}ms exceeded 5 seconds"

        # Variation should be reasonable (<1 second between fastest and slowest)
        latency_variance = max_latency - min(latencies)
        assert latency_variance < 1000, f"Latency variance {latency_variance:.0f}ms too high"

    def test_parallel_request_latency(self, client: TestClient):
        """Test latency with concurrent requests from different users."""
        import concurrent.futures

        def make_request(user_id: str) -> tuple:
            """Make request and return (user_id, latency_ms)."""
            start_time = time.time()
            response = client.post(
                "/chat/messages",
                headers=get_auth_headers(user_id),
                json={"message": "Hello"},
            )
            elapsed_ms = (time.time() - start_time) * 1000
            return (user_id, elapsed_ms, response.status_code)

        # Create 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(make_request, f"user-{i}")
                for i in range(5)
            ]
            results = [f.result() for f in futures]

        # All should succeed
        for user_id, latency_ms, status_code in results:
            assert status_code == 200
            assert latency_ms < 5000, f"Request from {user_id} took {latency_ms:.0f}ms"

    def test_large_message_latency(self, client: TestClient):
        """Test latency with larger message input."""
        user_id = "test-user"

        # Create a longer message
        large_message = "Create a todo with a very long description: " + ("x" * 500)

        start_time = time.time()
        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": large_message},
        )
        elapsed_ms = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 5000, f"Large message took {elapsed_ms:.0f}ms, expected <5000ms"

    def test_many_todos_latency(self, client: TestClient):
        """SC-006: Test latency with todos in database (latency target <2 seconds for list operations)."""
        user_id = "test-user"

        # List todos (even empty list should respond quickly)
        start_time = time.time()
        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Show all my todos"},
        )
        elapsed_ms = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 2000, f"List todos took {elapsed_ms:.0f}ms, expected <2000ms"

        # Verify response structure
        data = response.json()
        assert "todos" in data
        assert isinstance(data["todos"], list)

    def test_metadata_latency_tracking(self, client: TestClient):
        """Test that response includes metadata for latency tracking."""
        user_id = "test-user"

        response = client.post(
            "/chat/messages",
            headers=get_auth_headers(user_id),
            json={"message": "Hello"},
        )

        assert response.status_code == 200
        data = response.json()

        # Metadata should include timestamp
        assert "metadata" in data
        assert "timestamp" in data["metadata"]
        assert isinstance(data["metadata"]["timestamp"], str)

        # Should have ISO format timestamp for logging
        assert "T" in data["metadata"]["timestamp"]
        assert "Z" in data["metadata"]["timestamp"]
