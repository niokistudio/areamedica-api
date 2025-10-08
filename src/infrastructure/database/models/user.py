"""User SQLAlchemy models."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class UserModel(Base, TimestampMixin, SoftDeleteMixin):
    """User database model."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    permissions = relationship(
        "PermissionModel",
        secondary="user_permissions",
        primaryjoin="UserModel.id == UserPermissionModel.user_id",
        secondaryjoin="PermissionModel.id == UserPermissionModel.permission_id",
        back_populates="users",
        lazy="selectin",
    )
    created_transactions = relationship(
        "TransactionModel", back_populates="creator", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class PermissionModel(Base, TimestampMixin):
    """Permission database model."""

    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    users = relationship(
        "UserModel",
        secondary="user_permissions",
        primaryjoin="PermissionModel.id == UserPermissionModel.permission_id",
        secondaryjoin="UserModel.id == UserPermissionModel.user_id",
        back_populates="permissions",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name})>"


class UserPermissionModel(Base, TimestampMixin):
    """User-Permission association table."""

    __tablename__ = "user_permissions"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), primary_key=True, nullable=False
    )
    permission_id: Mapped[UUID] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True, nullable=False
    )
    granted_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    def __repr__(self) -> str:
        return f"<UserPermission(user_id={self.user_id}, permission_id={self.permission_id})>"
