"""User repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user import User


class IUserRepository(ABC):
    """User repository interface."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update existing user."""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Soft delete a user."""
        pass

    @abstractmethod
    async def list_active(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List active users with pagination."""
        pass

    @abstractmethod
    async def add_permission(self, user_id: UUID, permission_name: str) -> bool:
        """Add permission to user."""
        pass

    @abstractmethod
    async def remove_permission(self, user_id: UUID, permission_name: str) -> bool:
        """Remove permission from user."""
        pass
