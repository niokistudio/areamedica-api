"""Unit tests for AuthService."""

import pytest
from uuid import uuid4

from application.services.auth_service import AuthService
from domain.entities.user import User


class TestAuthService:
    """Test suite for AuthService."""

    @pytest.fixture
    def auth_service(self) -> AuthService:
        """Create AuthService instance."""
        return AuthService(
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )

    def test_password_hashing(self, auth_service: AuthService) -> None:
        """Test password hashing and verification."""
        password = "SuperSecret123!"
        hashed = auth_service.get_password_hash(password)

        assert hashed != password
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("WrongPassword", hashed)

    def test_create_access_token(self, auth_service: AuthService) -> None:
        """Test JWT token creation."""
        user_id = uuid4()
        email = "test@example.com"
        permissions = ["transaction:read", "transaction:create"]

        token = auth_service.create_access_token(user_id, email, permissions)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token(self, auth_service: AuthService) -> None:
        """Test JWT token verification."""
        user_id = uuid4()
        email = "test@example.com"
        permissions = ["transaction:read"]

        token = auth_service.create_access_token(user_id, email, permissions)
        payload = auth_service.verify_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
        assert payload["permissions"] == permissions

    def test_verify_invalid_token(self, auth_service: AuthService) -> None:
        """Test verification of invalid token."""
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.verify_token("invalid.token.here")

    def test_extract_user_id_from_token(self, auth_service: AuthService) -> None:
        """Test extracting user ID from token."""
        user_id = uuid4()
        token = auth_service.create_access_token(user_id, "test@example.com", [])

        extracted_id = auth_service.extract_user_id_from_token(token)
        assert extracted_id == user_id

    def test_has_required_permission(self, auth_service: AuthService) -> None:
        """Test permission checking."""
        from domain.entities.permission import Permission

        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed",
            full_name="Test User",
            is_active=True,
            permissions=[
                Permission(
                    id=uuid4(),
                    name="transaction:read",
                    description="Can read transactions",
                )
            ],
        )

        assert auth_service.has_required_permission(user, "transaction:read")
        assert not auth_service.has_required_permission(user, "transaction:delete")
