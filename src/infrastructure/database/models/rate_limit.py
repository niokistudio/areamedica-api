"""Rate limit SQLAlchemy model."""

from uuid import UUID, uuid4

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class RateLimitModel(Base, TimestampMixin):
    """Rate limit database model."""

    __tablename__ = "rate_limits"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    window_start: Mapped[str] = mapped_column(String, nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    def __repr__(self) -> str:
        return f"<RateLimit(resource_type={self.resource_type}, resource_id={self.resource_identifier}, count={self.request_count})>"
