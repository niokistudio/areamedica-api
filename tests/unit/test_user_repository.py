"""Unit tests for UserRepository."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.permission import Permission
from domain.entities.user import User
from infrastructure.database.repositories.user_repository import (
    SQLAlchemyUserRepository,
)


@pytest.mark.asyncio
class TestUserRepository:
    """Test suite for UserRepository."""

    @pytest.fixture
    def repository(self, db_session: AsyncSession) -> SQLAlchemyUserRepository:
        """Create repository instance."""
        return SQLAlchemyUserRepository(db_session)

    async def test_create_user(self, repository: SQLAlchemyUserRepository) -> None:
        """Test user creation."""
        user = User(
            id=uuid4(),
            email="new@example.com",
            password_hash="hashed_password",
            full_name="New User",
            national_id="V99887766",
            phone_number="04149998877",
            is_active=True,
        )

        created_user = await repository.create(user)

        assert created_user.id == user.id
        assert created_user.email == user.email
        assert created_user.full_name == user.full_name

    async def test_get_by_id(
        self, repository: SQLAlchemyUserRepository, test_user: dict
    ) -> None:
        """Test getting user by ID."""
        user = await repository.get_by_id(test_user["id"])

        assert user is not None
        assert user.email == test_user["email"]
        assert user.full_name == test_user["full_name"]

    async def test_get_by_email(
        self, repository: SQLAlchemyUserRepository, test_user: dict
    ) -> None:
        """Test getting user by email."""
        user = await repository.get_by_email(test_user["email"])

        assert user is not None
        assert user.id == test_user["id"]
        assert user.full_name == test_user["full_name"]

    async def test_get_nonexistent_user(
        self, repository: SQLAlchemyUserRepository
    ) -> None:
        """Test getting user that doesn't exist."""
        user = await repository.get_by_id(uuid4())

        assert user is None

    async def test_update_user(
        self, repository: SQLAlchemyUserRepository, test_user: dict
    ) -> None:
        """Test updating user."""
        user = await repository.get_by_id(test_user["id"])
        assert user is not None

        user.full_name = "Updated Name"
        updated_user = await repository.update(user)

        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == test_user["email"]

    async def test_delete_user(
        self, repository: SQLAlchemyUserRepository, test_user: dict
    ) -> None:
        """Test user deletion."""
        await repository.delete(test_user["id"])

        deleted_user = await repository.get_by_id(test_user["id"])
        assert deleted_user is None

    async def test_list_users(self, repository: SQLAlchemyUserRepository) -> None:
        """Test listing users."""
        users = await repository.list(limit=10, offset=0)

        assert isinstance(users, list)
        assert len(users) >= 0

    async def test_add_permission_to_user(
        self, repository: SQLAlchemyUserRepository, test_user: dict
    ) -> None:
        """Test adding permission to user."""
        permission = Permission(
            id=uuid4(),
            name="test:permission",
            description="Test permission",
        )

        user = await repository.get_by_id(test_user["id"])
        assert user is not None

        user.permissions.append(permission)
        updated_user = await repository.update(user)

        assert len(updated_user.permissions) > 0
        assert any(p.name == "test:permission" for p in updated_user.permissions)
