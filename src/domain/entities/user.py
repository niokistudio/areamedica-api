"""User domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from .permission import Permission


@dataclass
class User:
    """User entity."""

    id: UUID
    email: str
    password_hash: str
    full_name: str
    is_active: bool = True
    permissions: list[Permission] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission."""
        return any(p.name == permission_name for p in self.permissions)

    def is_deleted(self) -> bool:
        """Check if user is soft-deleted."""
        return self.deleted_at is not None

    def __str__(self) -> str:
        return f"{self.full_name} ({self.email})"
