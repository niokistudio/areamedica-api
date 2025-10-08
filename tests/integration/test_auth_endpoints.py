"""Integration tests for authentication endpoints."""

from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test suite for authentication endpoints."""

    async def test_register_user_success(self, client: AsyncClient) -> None:
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "full_name": "New User",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "password" not in data

    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user: dict
    ) -> None:
        """Test registration with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user["email"],
                "password": "AnotherPass123!",
                "full_name": "Another User",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    async def test_login_success(self, client: AsyncClient, test_user: dict) -> None:
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient) -> None:
        """Test login with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    async def test_get_current_user(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test getting current user information."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
        assert "permissions" in data

    async def test_get_current_user_unauthorized(self, client: AsyncClient) -> None:
        """Test accessing protected endpoint without authentication."""
        response = await client.get("/api/v1/auth/me")

        # 403 is returned when no credentials are provided (Forbidden)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_current_user_invalid_token(self, client: AsyncClient) -> None:
        """Test accessing protected endpoint with invalid token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        """Test registration with invalid email format."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePass123!",
                "full_name": "Test User",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_weak_password(self, client: AsyncClient) -> None:
        """Test registration with weak password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak",
                "full_name": "Test User",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
