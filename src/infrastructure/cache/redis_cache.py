"""Redis cache service."""

import json
import os
from typing import Any

import redis.asyncio as redis


class CacheService:
    """Asynchronous Redis cache service."""

    def __init__(self, redis_url: str | None = None) -> None:
        """Initialize cache service.

        Args:
            redis_url: Redis connection URL (defaults to env var REDIS_URL)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.from_url(
            self.redis_url, encoding="utf-8", decode_responses=True
        )

    async def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 300)

        Returns:
            True if successful, False otherwise
        """
        try:
            serialized_value = json.dumps(value, default=str)
            result = await self.redis_client.setex(key, ttl, serialized_value)
            return bool(result)
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.redis_client.delete(key)
            return bool(result)
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        try:
            result = await self.redis_client.exists(key)
            return bool(result)
        except Exception:
            return False

    def get_banesco_transaction_cache_key(self, transaction_id: str) -> str:
        """Generate cache key for Banesco transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Cache key
        """
        return f"banesco:transaction:{transaction_id}"

    def get_user_cache_key(self, user_id: str) -> str:
        """Generate cache key for user.

        Args:
            user_id: User ID

        Returns:
            Cache key
        """
        return f"user:{user_id}"

    async def close(self) -> None:
        """Close Redis connection."""
        await self.redis_client.close()

    async def __aenter__(self) -> "CacheService":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async context manager exit."""
        await self.close()
