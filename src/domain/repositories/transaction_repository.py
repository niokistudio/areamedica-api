"""Transaction repository interface."""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from domain.entities.transaction import Transaction, TransactionStatus


class ITransactionRepository(ABC):
    """Transaction repository interface."""

    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        """Get transaction by ID."""
        pass

    @abstractmethod
    async def get_by_transaction_id(self, transaction_id: str) -> Transaction | None:
        """Get transaction by transaction_id."""
        pass

    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction."""
        pass

    @abstractmethod
    async def update(self, transaction: Transaction) -> Transaction:
        """Update existing transaction."""
        pass

    @abstractmethod
    async def delete(self, transaction_id: UUID) -> bool:
        """Soft delete a transaction."""
        pass

    @abstractmethod
    async def list_with_filters(
        self,
        status: TransactionStatus | None = None,
        reference: str | None = None,
        phone: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Transaction], int]:
        """List transactions with filters and pagination. Returns (transactions, total_count)."""
        pass

    @abstractmethod
    async def update_status(
        self,
        transaction_id: UUID,
        old_status: TransactionStatus,
        new_status: TransactionStatus,
        reason: str | None = None,
        actor_id: UUID | None = None,
    ) -> bool:
        """Update transaction status and create audit event."""
        pass
