"""User repository implementation."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.entities.permission import Permission
from domain.entities.user import User
from domain.repositories.user_repository import IUserRepository
from infrastructure.database.models import PermissionModel, UserModel


class UserRepository(IUserRepository):
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity."""
        permissions = [
            Permission(
                id=p.id,
                name=p.name,
                description=p.description,
                created_at=p.created_at,
            )
            for p in model.permissions
        ]

        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            is_active=model.is_active,
            permissions=permissions,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to database model."""
        return UserModel(
            id=entity.id,
            email=entity.email,
            password_hash=entity.password_hash,
            full_name=entity.full_name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.permissions))
            .where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.permissions))
            .where(UserModel.email == email, UserModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, user: User) -> User:
        """Create a new user."""
        model = self._to_model(user)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model, ["permissions"])
        return self._to_entity(model)

    async def update(self, user: User) -> User:
        """Update existing user."""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"User with id {user.id} not found")

        model.email = user.email
        model.full_name = user.full_name
        model.is_active = user.is_active
        model.password_hash = user.password_hash

        await self.session.flush()
        await self.session.refresh(model, ["permissions"])
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        """Soft delete a user."""
        stmt = select(UserModel).where(
            UserModel.id == user_id, UserModel.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        model.soft_delete()
        await self.session.flush()
        return True

    async def list_active(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List active users with pagination."""
        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.permissions))
            .where(UserModel.deleted_at.is_(None), UserModel.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def add_permission(self, user_id: UUID, permission_name: str) -> bool:
        """Add permission to user."""
        # Get user
        user_stmt = select(UserModel).where(UserModel.id == user_id)
        user_result = await self.session.execute(user_stmt)
        user_model = user_result.scalar_one_or_none()

        if not user_model:
            return False

        # Get permission
        perm_stmt = select(PermissionModel).where(
            PermissionModel.name == permission_name
        )
        perm_result = await self.session.execute(perm_stmt)
        perm_model = perm_result.scalar_one_or_none()

        if not perm_model:
            return False

        # Add permission if not already present
        if perm_model not in user_model.permissions:
            user_model.permissions.append(perm_model)
            await self.session.flush()

        return True

    async def remove_permission(self, user_id: UUID, permission_name: str) -> bool:
        """Remove permission from user."""
        # Get user
        user_stmt = select(UserModel).where(UserModel.id == user_id)
        user_result = await self.session.execute(user_stmt)
        user_model = user_result.scalar_one_or_none()

        if not user_model:
            return False

        # Get permission
        perm_stmt = select(PermissionModel).where(
            PermissionModel.name == permission_name
        )
        perm_result = await self.session.execute(perm_stmt)
        perm_model = perm_result.scalar_one_or_none()

        if not perm_model:
            return False

        # Remove permission if present
        if perm_model in user_model.permissions:
            user_model.permissions.remove(perm_model)
            await self.session.flush()

        return True
