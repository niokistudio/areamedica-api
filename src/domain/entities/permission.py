"""Permission domain entity."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class PermissionType(str, Enum):
    """Permission types enumeration."""

    TRANSACTION_CREATE = "transaction:create"
    TRANSACTION_READ = "transaction:read"
    TRANSACTION_UPDATE = "transaction:update"
    TRANSACTION_DELETE = "transaction:delete"
    ADMIN_ACCESS = "admin:access"


@dataclass
class Permission:
    """Permission entity."""

    id: UUID
    name: str
    description: str | None = None
    created_at: datetime | None = None

    def __str__(self) -> str:
        return self.name
