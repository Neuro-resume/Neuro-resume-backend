"""Tests for user profile endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserProfile:
    """Tests for user profile operations."""

    async def test_get_profile_success(self, client: AsyncClient, auth_headers):
        """Test getting user profile."""
        response = await client.get("/v1/user/profile", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """Test getting profile without authentication."""
        response = await client.get("/v1/user/profile")
        assert response.status_code == 403

    async def test_update_profile_full_name(self, client: AsyncClient, auth_headers):
        """Test updating full name."""
        response = await client.patch(
            "/v1/user/profile",
            headers=auth_headers,
            json={"full_name": "John Doe"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "John Doe"

    async def test_update_profile_phone(self, client: AsyncClient, auth_headers):
        """Test updating phone number."""
        response = await client.patch(
            "/v1/user/profile",
            headers=auth_headers,
            json={"phone": "+1234567890"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+1234567890"

    async def test_update_profile_multiple_fields(
        self, client: AsyncClient, auth_headers
    ):
        """Test updating multiple fields at once."""
        update_data = {
            "full_name": "Jane Smith",
            "phone": "+9876543210",
            "location": "New York, USA",
        }

        response = await client.patch(
            "/v1/user/profile",
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["phone"] == update_data["phone"]
        assert data["location"] == update_data["location"]

    async def test_update_profile_empty_request(
        self, client: AsyncClient, auth_headers
    ):
        """Test update with no fields (should succeed but change nothing)."""
        # Get original profile
        original = await client.get("/v1/user/profile", headers=auth_headers)
        original_data = original.json()

        # Send empty update
        response = await client.patch(
            "/v1/user/profile",
            headers=auth_headers,
            json={},
        )

        assert response.status_code == 200
        data = response.json()
        # Profile should remain unchanged
        assert data["id"] == original_data["id"]
        assert data["username"] == original_data["username"]

    async def test_update_profile_unauthorized(self, client: AsyncClient):
        """Test updating profile without authentication."""
        response = await client.patch(
            "/v1/user/profile",
            json={"full_name": "Test"},
        )
        assert response.status_code == 403


@pytest.mark.asyncio
class TestChangePassword:
    """Tests for password change functionality."""

    async def test_change_password_success(
        self, client: AsyncClient, auth_headers, registered_user
    ):
        """Test successful password change."""
        response = await client.post(
            "/v1/user/change-password",
            headers=auth_headers,
            json={
                "old_password": registered_user["password"],
                "new_password": "newpassword123",
            },
        )

        assert response.status_code == 204

        # Verify can login with new password
        login_response = await client.post(
            "/v1/auth/login",
            json={
                "username": registered_user["user"]["username"],
                "password": "newpassword123",
            },
        )
        assert login_response.status_code == 200

    async def test_change_password_wrong_old_password(
        self, client: AsyncClient, auth_headers
    ):
        """Test password change with wrong old password."""
        response = await client.post(
            "/v1/user/change-password",
            headers=auth_headers,
            json={
                "old_password": "wrongpassword",
                "new_password": "newpassword123",
            },
        )

        assert response.status_code == 400
        assert "неверен" in response.text.lower() or "incorrect" in response.text.lower()

    async def test_change_password_short_new_password(
        self, client: AsyncClient, auth_headers, registered_user
    ):
        """Test password change with too short new password."""
        response = await client.post(
            "/v1/user/change-password",
            headers=auth_headers,
            json={
                "old_password": registered_user["password"],
                "new_password": "123",  # Too short
            },
        )

        assert response.status_code == 422

    async def test_change_password_unauthorized(self, client: AsyncClient):
        """Test password change without authentication."""
        response = await client.post(
            "/v1/user/change-password",
            json={
                "old_password": "oldpass",
                "new_password": "newpass123",
            },
        )
        assert response.status_code == 403

    async def test_change_password_missing_fields(
        self, client: AsyncClient, auth_headers
    ):
        """Test password change with missing fields."""
        response = await client.post(
            "/v1/user/change-password",
            headers=auth_headers,
            json={"old_password": "test123"},  # Missing new_password
        )
        assert response.status_code == 422
