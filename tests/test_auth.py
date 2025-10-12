"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthRegister:
    """Tests for user registration."""

    async def test_register_success(self, client: AsyncClient, test_user_data):
        """Test successful user registration."""
        response = await client.post("/v1/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()

        assert "token" in data
        assert "user" in data
        assert data["user"]["username"] == test_user_data["username"]
        assert data["user"]["email"] == test_user_data["email"]
        assert "password" not in data["user"]
        assert "password_hash" not in data["user"]

    async def test_register_duplicate_username(
        self, client: AsyncClient, test_user_data, test_user_data_2
    ):
        """Test registration with duplicate username."""
        # Register first user
        response1 = await client.post("/v1/auth/register", json=test_user_data)
        assert response1.status_code == 201

        # Try to register with same username but different email
        duplicate_data = test_user_data_2.copy()
        duplicate_data["username"] = test_user_data["username"]

        response2 = await client.post("/v1/auth/register", json=duplicate_data)
        assert response2.status_code == 409
        assert "username" in response2.text.lower()

    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user_data, test_user_data_2
    ):
        """Test registration with duplicate email."""
        # Register first user
        response1 = await client.post("/v1/auth/register", json=test_user_data)
        assert response1.status_code == 201

        # Try to register with same email but different username
        duplicate_data = test_user_data_2.copy()
        duplicate_data["email"] = test_user_data["email"]

        response2 = await client.post("/v1/auth/register", json=duplicate_data)
        assert response2.status_code == 409
        assert "email" in response2.text.lower()

    async def test_register_invalid_email(self, client: AsyncClient, test_user_data):
        """Test registration with invalid email."""
        invalid_data = test_user_data.copy()
        invalid_data["email"] = "not-an-email"

        response = await client.post("/v1/auth/register", json=invalid_data)
        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient, test_user_data):
        """Test registration with short password."""
        invalid_data = test_user_data.copy()
        invalid_data["password"] = "12345"  # Less than 6 characters

        response = await client.post("/v1/auth/register", json=invalid_data)
        assert response.status_code == 422

    async def test_register_missing_fields(self, client: AsyncClient):
        """Test registration with missing required fields."""
        response = await client.post(
            "/v1/auth/register",
            json={"username": "test"},  # Missing email and password
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestAuthLogin:
    """Tests for user login."""

    async def test_login_success(self, client: AsyncClient, registered_user):
        """Test successful login."""
        response = await client.post(
            "/v1/auth/login",
            json={
                "username": registered_user["user"]["username"],
                "password": registered_user["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "token" in data
        assert "user" in data
        assert data["user"]["id"] == registered_user["user"]["id"]

    async def test_login_wrong_password(self, client: AsyncClient, registered_user):
        """Test login with wrong password."""
        response = await client.post(
            "/v1/auth/login",
            json={
                "username": registered_user["user"]["username"],
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent username."""
        response = await client.post(
            "/v1/auth/login",
            json={"username": "nonexistent", "password": "password123"},
        )

        assert response.status_code == 401

    async def test_login_missing_credentials(self, client: AsyncClient):
        """Test login with missing credentials."""
        response = await client.post("/v1/auth/login", json={"username": "test"})
        assert response.status_code == 422


@pytest.mark.asyncio
class TestAuthToken:
    """Tests for token operations."""

    async def test_refresh_token(self, client: AsyncClient, auth_headers):
        """Test token refresh."""
        response = await client.post("/v1/auth/refresh", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "token" in data
        assert "user" in data

    async def test_refresh_token_unauthorized(self, client: AsyncClient):
        """Test token refresh without authentication."""
        response = await client.post("/v1/auth/refresh")
        assert response.status_code == 403  # No credentials provided

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test token refresh with invalid token."""
        response = await client.post(
            "/v1/auth/refresh", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    async def test_logout(self, client: AsyncClient, auth_headers):
        """Test logout."""
        response = await client.post("/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 204
