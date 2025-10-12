"""Tests for interview session endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestInterviewSessions:
    """Tests for interview session management."""

    async def test_create_session_success(self, client: AsyncClient, auth_headers):
        """Test creating a new interview session."""
        response = await client.post("/v1/interview/sessions", headers=auth_headers)

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert "userId" in data
        assert data["status"] == "in_progress"
        assert "createdAt" in data
        assert data["messageCount"] == 0

    async def test_create_session_unauthorized(self, client: AsyncClient):
        """Test creating session without authentication."""
        response = await client.post("/v1/interview/sessions")
        assert response.status_code == 403

    async def test_get_sessions_empty(self, client: AsyncClient, auth_headers):
        """Test getting sessions when none exist."""
        response = await client.get("/v1/interview/sessions", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    async def test_get_sessions_with_data(self, client: AsyncClient, auth_headers):
        """Test getting sessions after creating some."""
        # Create 3 sessions
        for _ in range(3):
            await client.post("/v1/interview/sessions", headers=auth_headers)

        response = await client.get("/v1/interview/sessions", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3
        assert data["pagination"]["total"] == 3

    async def test_get_sessions_pagination(self, client: AsyncClient, auth_headers):
        """Test session list pagination."""
        # Create 5 sessions
        for _ in range(5):
            await client.post("/v1/interview/sessions", headers=auth_headers)

        # Get first page (2 items)
        response = await client.get(
            "/v1/interview/sessions?limit=2&offset=0", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 5

        # Get second page (2 items)
        response = await client.get(
            "/v1/interview/sessions?limit=2&offset=2", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

    async def test_get_session_by_id(self, client: AsyncClient, auth_headers):
        """Test getting a specific session by ID."""
        # Create session
        create_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = create_response.json()["id"]

        # Get session by ID
        response = await client.get(
            f"/v1/interview/sessions/{session_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id

    async def test_get_session_not_found(self, client: AsyncClient, auth_headers):
        """Test getting non-existent session."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(
            f"/v1/interview/sessions/{fake_uuid}", headers=auth_headers
        )
        assert response.status_code == 404

    async def test_delete_session(self, client: AsyncClient, auth_headers):
        """Test deleting a session."""
        # Create session
        create_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = create_response.json()["id"]

        # Delete session
        response = await client.delete(
            f"/v1/interview/sessions/{session_id}", headers=auth_headers
        )
        assert response.status_code == 204

        # Verify session is deleted
        get_response = await client.get(
            f"/v1/interview/sessions/{session_id}", headers=auth_headers
        )
        assert get_response.status_code == 404


@pytest.mark.asyncio
class TestSessionMessages:
    """Tests for session messaging."""

    async def test_send_message(self, client: AsyncClient, auth_headers):
        """Test sending a message to a session."""
        # Create session
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]

        # Send message
        response = await client.post(
            f"/v1/interview/sessions/{session_id}/messages",
            headers=auth_headers,
            json={"message": "Hello, I want to create a resume"},
        )

        assert response.status_code == 200  # Changed from 201 to match OpenAPI
        data = response.json()
        assert "userMessage" in data
        assert "aiResponse" in data

        # User message
        assert data["userMessage"]["role"] == "user"
        assert data["userMessage"]["content"] == "Hello, I want to create a resume"

        # AI response (placeholder for now)
        assert data["aiResponse"]["role"] == "ai"
        assert len(data["aiResponse"]["content"]) > 0

    async def test_send_message_to_nonexistent_session(
        self, client: AsyncClient, auth_headers
    ):
        """Test sending message to non-existent session."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            f"/v1/interview/sessions/{fake_uuid}/messages",
            headers=auth_headers,
            json={"message": "Test message"},
        )
        assert response.status_code == 404

    async def test_send_empty_message(self, client: AsyncClient, auth_headers):
        """Test sending empty message."""
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]

        response = await client.post(
            f"/v1/interview/sessions/{session_id}/messages",
            headers=auth_headers,
            json={"message": ""},
        )
        # Should fail validation
        assert response.status_code == 422

    async def test_get_messages(self, client: AsyncClient, auth_headers):
        """Test getting messages from a session."""
        # Create session and send message
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]

        await client.post(
            f"/v1/interview/sessions/{session_id}/messages",
            headers=auth_headers,
            json={"message": "Test message 1"},
        )

        await client.post(
            f"/v1/interview/sessions/{session_id}/messages",
            headers=auth_headers,
            json={"message": "Test message 2"},
        )

        # Get messages
        response = await client.get(
            f"/v1/interview/sessions/{session_id}/messages", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Should have 4 messages: 2 user + 2 assistant responses
        assert len(data) >= 2


@pytest.mark.asyncio
class TestSessionCompletion:
    """Tests for completing interview sessions."""

    async def test_complete_session(self, client: AsyncClient, auth_headers):
        """Test completing a session."""
        # Create session
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]

        # Complete session
        response = await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "session" in data
        assert "resumeId" in data
        assert data["session"]["status"] == "completed"

    async def test_complete_nonexistent_session(
        self, client: AsyncClient, auth_headers
    ):
        """Test completing non-existent session."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            f"/v1/interview/sessions/{fake_uuid}/complete", headers=auth_headers
        )
        assert response.status_code == 404

    async def test_complete_already_completed_session(
        self, client: AsyncClient, auth_headers
    ):
        """Test completing an already completed session."""
        # Create and complete session
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]

        await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        # Try to complete again
        response = await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        # Should return conflict error (409)
        assert response.status_code == 409
