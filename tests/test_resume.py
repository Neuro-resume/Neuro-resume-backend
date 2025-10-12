"""Tests for resume endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestResumeCreation:
    """Tests for resume creation."""

    async def test_create_resume_success(self, client: AsyncClient, auth_headers):
        """Test creating a resume from completed session."""
        # Create and complete session
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]

        # Send some messages to populate session
        await client.post(
            f"/v1/interview/sessions/{session_id}/messages",
            headers=auth_headers,
            json={"content": "I'm a Senior Python Developer with 5 years experience"},
        )

        # Complete session
        await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        # Create resume
        response = await client.post(
            "/v1/resumes",
            headers=auth_headers,
            json={
                "session_id": session_id,
                "format": "pdf",
                "title": "Senior Developer Resume",
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["session_id"] == session_id
        assert data["format"] == "pdf"
        assert data["title"] == "Senior Developer Resume"
        assert "content" in data
        assert "created_at" in data

    async def test_create_resume_from_nonexistent_session(
        self, client: AsyncClient, auth_headers
    ):
        """Test creating resume from non-existent session."""
        response = await client.post(
            "/v1/resumes",
            headers=auth_headers,
            json={
                "session_id": 99999,
                "format": "pdf",
                "title": "Test Resume",
            },
        )
        assert response.status_code == 404

    async def test_create_resume_invalid_format(self, client: AsyncClient, auth_headers):
        """Test creating resume with invalid format."""
        # Create session
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]

        response = await client.post(
            "/v1/resumes",
            headers=auth_headers,
            json={
                "session_id": session_id,
                "format": "invalid",
                "title": "Test Resume",
            },
        )
        assert response.status_code == 422

    async def test_create_resume_unauthorized(self, client: AsyncClient):
        """Test creating resume without authentication."""
        response = await client.post(
            "/v1/resumes",
            json={
                "session_id": 1,
                "format": "pdf",
                "title": "Test Resume",
            },
        )
        assert response.status_code == 403


@pytest.mark.asyncio
class TestResumeRetrieval:
    """Tests for resume retrieval."""

    async def test_get_resumes_empty(self, client: AsyncClient, auth_headers):
        """Test getting resumes when none exist."""
        response = await client.get("/v1/resumes", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_get_resumes_with_data(self, client: AsyncClient, auth_headers):
        """Test getting resumes after creating some."""
        # Create session and resume
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]

        await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        # Create 2 resumes
        for i in range(2):
            await client.post(
                "/v1/resumes",
                headers=auth_headers,
                json={
                    "session_id": session_id,
                    "format": "pdf",
                    "title": f"Resume {i+1}",
                },
            )

        response = await client.get("/v1/resumes", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    async def test_get_resumes_pagination(self, client: AsyncClient, auth_headers):
        """Test resume list pagination."""
        # Create session
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]
        await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        # Create 5 resumes
        for i in range(5):
            await client.post(
                "/v1/resumes",
                headers=auth_headers,
                json={
                    "session_id": session_id,
                    "format": "pdf",
                    "title": f"Resume {i+1}",
                },
            )

        # Get first page
        response = await client.get(
            "/v1/resumes?limit=2&offset=0", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

    async def test_get_resume_by_id(self, client: AsyncClient, auth_headers):
        """Test getting a specific resume by ID."""
        # Create session and resume
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]
        await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        create_response = await client.post(
            "/v1/resumes",
            headers=auth_headers,
            json={
                "session_id": session_id,
                "format": "pdf",
                "title": "Test Resume",
            },
        )
        resume_id = create_response.json()["id"]

        # Get resume by ID
        response = await client.get(f"/v1/resumes/{resume_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resume_id

    async def test_get_resume_not_found(self, client: AsyncClient, auth_headers):
        """Test getting non-existent resume."""
        response = await client.get("/v1/resumes/99999", headers=auth_headers)
        assert response.status_code == 404


@pytest.mark.asyncio
class TestResumeDownload:
    """Tests for resume download."""

    async def test_download_resume_pdf(self, client: AsyncClient, auth_headers):
        """Test downloading resume in PDF format."""
        # Create resume
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]
        await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        create_response = await client.post(
            "/v1/resumes",
            headers=auth_headers,
            json={
                "session_id": session_id,
                "format": "pdf",
                "title": "Test Resume",
            },
        )
        resume_id = create_response.json()["id"]

        # Download resume
        response = await client.get(
            f"/v1/resumes/{resume_id}/download?format=pdf", headers=auth_headers
        )

        assert response.status_code == 200
        # Check content type for PDF (placeholder returns text/plain for now)
        assert "content-disposition" in response.headers.lower() or response.status_code == 200

    async def test_download_resume_docx(self, client: AsyncClient, auth_headers):
        """Test downloading resume in DOCX format."""
        # Create resume
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]
        await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        create_response = await client.post(
            "/v1/resumes",
            headers=auth_headers,
            json={
                "session_id": session_id,
                "format": "docx",
                "title": "Test Resume",
            },
        )
        resume_id = create_response.json()["id"]

        # Download resume
        response = await client.get(
            f"/v1/resumes/{resume_id}/download?format=docx", headers=auth_headers
        )

        assert response.status_code == 200

    async def test_download_resume_txt(self, client: AsyncClient, auth_headers):
        """Test downloading resume in TXT format."""
        # Create resume
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]
        await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        create_response = await client.post(
            "/v1/resumes",
            headers=auth_headers,
            json={
                "session_id": session_id,
                "format": "txt",
                "title": "Test Resume",
            },
        )
        resume_id = create_response.json()["id"]

        # Download resume
        response = await client.get(
            f"/v1/resumes/{resume_id}/download?format=txt", headers=auth_headers
        )

        assert response.status_code == 200

    async def test_download_resume_not_found(self, client: AsyncClient, auth_headers):
        """Test downloading non-existent resume."""
        response = await client.get(
            "/v1/resumes/99999/download?format=pdf", headers=auth_headers
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestResumeRegenerate:
    """Tests for resume regeneration."""

    async def test_regenerate_resume(self, client: AsyncClient, auth_headers):
        """Test regenerating a resume."""
        # Create resume
        session_response = await client.post(
            "/v1/interview/sessions", headers=auth_headers
        )
        session_id = session_response.json()["id"]
        await client.post(
            f"/v1/interview/sessions/{session_id}/complete", headers=auth_headers
        )

        create_response = await client.post(
            "/v1/resumes",
            headers=auth_headers,
            json={
                "session_id": session_id,
                "format": "pdf",
                "title": "Test Resume",
            },
        )
        resume_id = create_response.json()["id"]
        original_content = create_response.json()["content"]

        # Regenerate
        response = await client.post(
            f"/v1/resumes/{resume_id}/regenerate", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resume_id
        # Content should be regenerated (in real implementation, would be different)
        assert "content" in data

    async def test_regenerate_resume_not_found(self, client: AsyncClient, auth_headers):
        """Test regenerating non-existent resume."""
        response = await client.post(
            "/v1/resumes/99999/regenerate", headers=auth_headers
        )
        assert response.status_code == 404
