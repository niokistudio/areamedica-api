"""Unit tests for UserRepository."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from domain.entities.user import User
from infrastructure.database.repositories.user_repository import UserRepository


@pytest.mark.asyncio
class TestUserRepository:
    """Test suite for UserRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock()

    @pytest.fixture
    def repository(self, mock_session) -> UserRepository:
        """Create repository instance with mock session."""
        return UserRepository(mock_session)

    async def test_create_user(self, repository: UserRepository, mock_session) -> None:
        """Test user creation."""
        user = User(
            id=uuid4(),
            email="new@example.com",
            password_hash="hashed_password",
            full_name="New User",
            is_active=True,
        )

        # Mock the flush and refresh methods
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        created_user = await repository.create(user)

        assert created_user.id == user.id
        assert created_user.email == user.email
        assert created_user.full_name == user.full_name
        mock_session.flush.assert_called_once()

    async def test_get_by_id(self, repository: UserRepository, mock_session) -> None:
        """Test getting user by ID."""
        user_id = uuid4()

        # Mock the execute method
        mock_result = Mock()
        mock_model = Mock()
        mock_model.permissions = []  # Empty list of permissions
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # The method will try to convert the model to entity
        await repository.get_by_id(user_id)

        mock_session.execute.assert_called_once()

    async def test_get_by_email(self, repository: UserRepository, mock_session) -> None:
        """Test getting user by email."""
        email = "test@example.com"

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_by_email(email)

        assert result is None
        mock_session.execute.assert_called_once()

    async def test_update_user(self, repository: UserRepository, mock_session) -> None:
        """Test updating user."""
        user = User(
            id=uuid4(),
            email="update@example.com",
            password_hash="hashed",
            full_name="Update User",
            is_active=True,
        )

        # Mock execute to return a result with the updated model
        mock_result = Mock()
        mock_model = Mock()
        mock_model.permissions = []
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        await repository.update(user)

        # Verify execute was called (for the SELECT statement)
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()

    async def test_delete_user(self, repository: UserRepository, mock_session) -> None:
        """Test user deletion."""
        user_id = uuid4()

        mock_result = Mock()
        mock_model = Mock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        result = await repository.delete(user_id)

        assert result is True
        mock_session.flush.assert_called_once()

    async def test_list_active_users(
        self, repository: UserRepository, mock_session
    ) -> None:
        """Test listing active users."""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        users = await repository.list_active(skip=0, limit=10)

        assert isinstance(users, list)
        mock_session.execute.assert_called_once()

    async def test_add_permission_to_user(
        self, repository: UserRepository, mock_session
    ) -> None:
        """Test adding permission to user."""
        user_id = uuid4()
        permission_name = "test:permission"

        mock_result = Mock()
        mock_user_model = Mock()
        mock_user_model.permissions = []
        mock_result.scalar_one_or_none.return_value = mock_user_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        result = await repository.add_permission(user_id, permission_name)

        assert result is True
        mock_session.flush.assert_called_once()
