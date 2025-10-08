"""Transaction service."""

from datetime import datetime
from uuid import UUID, uuid4

from domain.entities.transaction import (
    BankType,
    Transaction,
    TransactionStatus,
    TransactionType,
)
from domain.repositories.transaction_repository import ITransactionRepository


class TransactionService:
    """Business logic for transactions."""

    def __init__(self, transaction_repo: ITransactionRepository) -> None:
        self.transaction_repo = transaction_repo

    async def create_or_update_transaction(
        self,
        transaction_id: str,
        reference: str,
        bank: BankType,
        transaction_type: TransactionType,
        customer_full_name: str,
        customer_phone: str,
        customer_national_id: str,
        concept: str | None = None,
        banesco_payload: dict | None = None,
        created_by: UUID | None = None,
    ) -> Transaction:
        """Create a new transaction or update existing one."""
        # Check if transaction already exists
        existing_transaction = await self.transaction_repo.get_by_transaction_id(
            transaction_id
        )

        if existing_transaction:
            # Update existing transaction
            existing_transaction.reference = reference
            existing_transaction.customer_full_name = customer_full_name
            existing_transaction.customer_phone = customer_phone
            existing_transaction.customer_national_id = customer_national_id
            existing_transaction.concept = concept
            existing_transaction.banesco_payload = banesco_payload
            existing_transaction.bank = bank
            existing_transaction.transaction_type = transaction_type

            return await self.transaction_repo.update(existing_transaction)

        # Create new transaction
        new_transaction = Transaction(
            id=uuid4(),
            transaction_id=transaction_id,
            status=TransactionStatus.IN_PROGRESS,
            bank=bank,
            transaction_type=transaction_type,
            reference=reference,
            customer_full_name=customer_full_name,
            customer_phone=customer_phone,
            customer_national_id=customer_national_id,
            concept=concept,
            banesco_payload=banesco_payload,
            created_by=created_by,
        )

        return await self.transaction_repo.create(new_transaction)

    async def get_transaction_by_id(self, transaction_id: UUID) -> Transaction | None:
        """Get transaction by ID."""
        return await self.transaction_repo.get_by_id(transaction_id)

    async def get_transaction_by_transaction_id(
        self, transaction_id: str
    ) -> Transaction | None:
        """Get transaction by transaction_id."""
        return await self.transaction_repo.get_by_transaction_id(transaction_id)

    async def get_transaction_by_reference(
        self, reference: str
    ) -> Transaction | None:
        """Get transaction by reference number."""
        return await self.transaction_repo.get_by_reference(reference)

    async def update_transaction_status(
        self,
        transaction_id: UUID,
        new_status: TransactionStatus,
        reason: str | None = None,
        actor_id: UUID | None = None,
    ) -> bool:
        """Update transaction status with audit trail."""
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            return False

        old_status = transaction.status

        return await self.transaction_repo.update_status(
            transaction_id=transaction_id,
            old_status=old_status,
            new_status=new_status,
            reason=reason,
            actor_id=actor_id,
        )

    async def list_transactions(
        self,
        status: TransactionStatus | None = None,
        bank: BankType | None = None,
        transaction_type: TransactionType | None = None,
        reference: str | None = None,
        phone: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Transaction], int]:
        """List transactions with filters and pagination.

        Returns:
            Tuple of (transactions, total_count)
        """
        transactions, total = await self.transaction_repo.list_with_filters(
            status=status,
            reference=reference,
            phone=phone,
            from_date=from_date,
            to_date=to_date,
            skip=offset,
            limit=limit,
        )

        return transactions, total

    async def delete_transaction(self, transaction_id: UUID) -> bool:
        """Soft delete a transaction."""
        return await self.transaction_repo.delete(transaction_id)
