"""Authentication service."""

import os
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from domain.entities.user import User


class AuthService:
    """Authentication service for handling JWT and password operations."""

    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ) -> None:
        self.secret_key = secret_key or os.getenv("SECRET_KEY", "your-secret-key-here")
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def create_access_token(
        self, user_id: UUID, email: str, permissions: list[str] | None = None
    ) -> str:
        """Create JWT access token."""
        to_encode = {
            "sub": str(user_id),
            "email": email,
            "permissions": permissions or [],
        }
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}") from e

    def extract_user_id_from_token(self, token: str) -> UUID:
        """Extract user ID from JWT token."""
        payload = self.verify_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise ValueError("Token does not contain user ID")
        return UUID(user_id_str)

    def has_required_permission(self, user: User, required_permission: str) -> bool:
        """Check if user has required permission."""
        return user.has_permission(required_permission)
