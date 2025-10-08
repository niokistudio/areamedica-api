"""Transaction repository implementation."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.transaction import (
    BankType,
    Transaction,
    TransactionStatus,
    TransactionType,
)
from domain.repositories.transaction_repository import ITransactionRepository
from infrastructure.database.models import (
    BankTypeEnum,
    TransactionEventModel,
    TransactionModel,
    TransactionStatusEnum,
    TransactionTypeEnum,
)


class TransactionRepository(ITransactionRepository):
    """SQLAlchemy implementation of transaction repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: TransactionModel) -> Transaction:
        """Convert database model to domain entity."""
        return Transaction(
            id=model.id,
            transaction_id=model.transaction_id,
            status=TransactionStatus(model.status.value),
            bank=BankType(model.bank.value),
            transaction_type=TransactionType(model.transaction_type.value),
            reference=model.reference,
            customer_full_name=model.customer_full_name,
            customer_phone=model.customer_phone,
            customer_national_id=model.customer_national_id,
            concept=model.concept,
            banesco_payload=model.banesco_payload,
            extra_data=model.extra_data,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            created_by=model.created_by,
        )

    def _to_model(self, entity: Transaction) -> TransactionModel:
        """Convert domain entity to database model."""
        return TransactionModel(
            id=entity.id,
            transaction_id=entity.transaction_id,
            status=TransactionStatusEnum(entity.status.value),
            bank=BankTypeEnum(entity.bank.value),
            transaction_type=TransactionTypeEnum(entity.transaction_type.value),
            reference=entity.reference,
            customer_full_name=entity.customer_full_name,
            customer_phone=entity.customer_phone,
            customer_national_id=entity.customer_national_id,
            concept=entity.concept,
            banesco_payload=entity.banesco_payload,
            extra_data=entity.extra_data,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            created_by=entity.created_by,
        )

    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        """Get transaction by ID."""
        stmt = select(TransactionModel).where(
            TransactionModel.id == transaction_id, TransactionModel.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_transaction_id(self, transaction_id: str) -> Transaction | None:
        """Get transaction by transaction_id."""
        stmt = select(TransactionModel).where(
            TransactionModel.transaction_id == transaction_id,
            TransactionModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_reference(self, reference: str) -> Transaction | None:
        """Get transaction by reference number."""
        stmt = select(TransactionModel).where(
            TransactionModel.reference == reference,
            TransactionModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction."""
        model = self._to_model(transaction)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, transaction: Transaction) -> Transaction:
        """Update existing transaction."""
        stmt = select(TransactionModel).where(TransactionModel.id == transaction.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Transaction with id {transaction.id} not found")

        model.status = TransactionStatusEnum(transaction.status.value)
        model.bank = BankTypeEnum(transaction.bank.value)
        model.transaction_type = TransactionTypeEnum(transaction.transaction_type.value)
        model.reference = transaction.reference
        model.customer_full_name = transaction.customer_full_name
        model.customer_phone = transaction.customer_phone
        model.customer_national_id = transaction.customer_national_id
        model.concept = transaction.concept
        model.banesco_payload = transaction.banesco_payload
        model.extra_data = transaction.extra_data

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, transaction_id: UUID) -> bool:
        """Soft delete a transaction."""
        stmt = select(TransactionModel).where(
            TransactionModel.id == transaction_id, TransactionModel.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        model.soft_delete()
        await self.session.flush()
        return True

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
        """List transactions with filters and pagination."""
        # Build base query
        conditions = [TransactionModel.deleted_at.is_(None)]

        if status:
            conditions.append(
                TransactionModel.status == TransactionStatusEnum(status.value)
            )
        if reference:
            conditions.append(TransactionModel.reference == reference)
        if phone:
            conditions.append(TransactionModel.customer_phone == phone)
        if from_date:
            conditions.append(TransactionModel.created_at >= from_date)
        if to_date:
            conditions.append(TransactionModel.created_at <= to_date)

        # Count total
        count_stmt = (
            select(func.count()).select_from(TransactionModel).where(*conditions)
        )
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get transactions
        stmt = (
            select(TransactionModel)
            .where(*conditions)
            .order_by(TransactionModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        transactions = [self._to_entity(model) for model in models]
        return transactions, total

    async def update_status(
        self,
        transaction_id: UUID,
        old_status: TransactionStatus,
        new_status: TransactionStatus,
        reason: str | None = None,
        actor_id: UUID | None = None,
    ) -> bool:
        """Update transaction status and create audit event."""
        # Get transaction
        stmt = select(TransactionModel).where(TransactionModel.id == transaction_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        # Update status
        model.status = TransactionStatusEnum(new_status.value)

        # Create audit event
        event = TransactionEventModel(
            transaction_id=transaction_id,
            old_status=TransactionStatusEnum(old_status.value),
            new_status=TransactionStatusEnum(new_status.value),
            reason=reason,
            actor_type="USER" if actor_id else "SYSTEM",
            actor_id=actor_id,
            metadata={},
        )
        self.session.add(event)

        await self.session.flush()
        return True
