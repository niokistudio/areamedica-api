"""Rate limiting service for Banesco API calls."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models import RateLimitModel


class RateLimitService:
    """Service for managing API rate limits."""

    def __init__(self, session: AsyncSession, banesco_rate_limit: int = 2) -> None:
        """Initialize rate limit service.

        Args:
            session: Database session
            banesco_rate_limit: Max requests per minute per transaction_id (default: 2)
        """
        self.session = session
        self.banesco_rate_limit = banesco_rate_limit

    async def check_rate_limit(
        self, resource_type: str, resource_identifier: str
    ) -> bool:
        """Check if request is within rate limit.

        Args:
            resource_type: Type of resource (e.g., 'TRANSACTION_ID')
            resource_identifier: Identifier for the resource

        Returns:
            True if within limit, False if limit exceeded
        """
        now = datetime.utcnow()
        window_start = now.replace(second=0, microsecond=0)

        current_count = await self._get_request_count(
            resource_type, resource_identifier, window_start
        )

        if resource_type == "TRANSACTION_ID":
            return current_count < self.banesco_rate_limit

        return True

    async def increment_rate_limit(
        self, resource_type: str, resource_identifier: str
    ) -> None:
        """Increment rate limit counter.

        Args:
            resource_type: Type of resource (e.g., 'TRANSACTION_ID')
            resource_identifier: Identifier for the resource
        """
        now = datetime.utcnow()
        window_start = now.replace(second=0, microsecond=0)

        # Try to get existing rate limit record
        stmt = select(RateLimitModel).where(
            RateLimitModel.resource_type == resource_type,
            RateLimitModel.resource_identifier == resource_identifier,
            RateLimitModel.window_start == window_start.isoformat(),
        )
        result = await self.session.execute(stmt)
        rate_limit = result.scalar_one_or_none()

        if rate_limit:
            # Increment existing counter
            rate_limit.request_count += 1
        else:
            # Create new counter
            rate_limit = RateLimitModel(
                resource_type=resource_type,
                resource_identifier=resource_identifier,
                window_start=window_start.isoformat(),
                request_count=1,
            )
            self.session.add(rate_limit)

        await self.session.flush()

    async def _get_request_count(
        self, resource_type: str, resource_identifier: str, window_start: datetime
    ) -> int:
        """Get current request count for the given window.

        Args:
            resource_type: Type of resource
            resource_identifier: Identifier for the resource
            window_start: Start of the time window

        Returns:
            Current request count
        """
        stmt = select(RateLimitModel).where(
            RateLimitModel.resource_type == resource_type,
            RateLimitModel.resource_identifier == resource_identifier,
            RateLimitModel.window_start == window_start.isoformat(),
        )
        result = await self.session.execute(stmt)
        rate_limit = result.scalar_one_or_none()

        return rate_limit.request_count if rate_limit else 0

    async def reset_rate_limit(
        self, resource_type: str, resource_identifier: str
    ) -> None:
        """Reset rate limit for a resource (useful for testing).

        Args:
            resource_type: Type of resource
            resource_identifier: Identifier for the resource
        """
        now = datetime.utcnow()
        window_start = now.replace(second=0, microsecond=0)

        stmt = select(RateLimitModel).where(
            RateLimitModel.resource_type == resource_type,
            RateLimitModel.resource_identifier == resource_identifier,
            RateLimitModel.window_start == window_start.isoformat(),
        )
        result = await self.session.execute(stmt)
        rate_limit = result.scalar_one_or_none()

        if rate_limit:
            await self.session.delete(rate_limit)
            await self.session.flush()
