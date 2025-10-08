"""Unit tests for TransactionService."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from application.services.transaction_service import TransactionService
from domain.entities.transaction import (
    BankType,
    Transaction,
    TransactionStatus,
    TransactionType,
)


class TestTransactionService:
    """Test suite for TransactionService."""

    @pytest.fixture
    def mock_repo(self) -> Mock:
        """Create mock transaction repository."""
        return Mock()

    @pytest.fixture
    def service(self, mock_repo: Mock) -> TransactionService:
        """Create TransactionService instance."""
        return TransactionService(transaction_repo=mock_repo)

    @pytest.mark.asyncio
    async def test_create_transaction(
        self, service: TransactionService, mock_repo: Mock
    ) -> None:
        """Test transaction creation."""
        user_id = uuid4()
        transaction_id = "TEST-123"
        mock_repo.get_by_transaction_id = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(
            return_value=Transaction(
                id=uuid4(),
                transaction_id=transaction_id,
                status=TransactionStatus.IN_PROGRESS,
                bank=BankType.BANESCO,
                transaction_type=TransactionType.TRANSACTION,
                reference="REF123",
                customer_full_name="Juan Pérez",
                customer_phone="04161234567",
                customer_national_id="V12345678",
                concept="Pago de consulta",
                created_by=user_id,
                created_at=datetime.utcnow(),
            )
        )

        transaction = await service.create_or_update_transaction(
            transaction_id=transaction_id,
            reference="REF123",
            bank=BankType.BANESCO,
            transaction_type=TransactionType.TRANSACTION,
            customer_full_name="Juan Pérez",
            customer_phone="04161234567",
            customer_national_id="V12345678",
            concept="Pago de consulta",
            created_by=user_id,
        )

        assert transaction.transaction_id == transaction_id
        assert transaction.reference == "REF123"
        assert transaction.status == TransactionStatus.IN_PROGRESS
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_existing_transaction(
        self, service: TransactionService, mock_repo: Mock
    ) -> None:
        """Test updating an existing transaction."""
        transaction_id = "TEST-123"
        existing_transaction = Transaction(
            id=uuid4(),
            transaction_id=transaction_id,
            status=TransactionStatus.IN_PROGRESS,
            bank=BankType.BANESCO,
            transaction_type=TransactionType.TRANSACTION,
            reference="OLD-REF",
            customer_full_name="Juan Pérez",
            customer_phone="04161234567",
            customer_national_id="V12345678",
            concept="Concepto antiguo",
            created_at=datetime.utcnow(),
        )

        mock_repo.get_by_transaction_id = AsyncMock(return_value=existing_transaction)
        mock_repo.update = AsyncMock(return_value=existing_transaction)

        transaction = await service.create_or_update_transaction(
            transaction_id=transaction_id,
            reference="NEW-REF",
            bank=BankType.BANESCO,
            transaction_type=TransactionType.TRANSACTION,
            customer_full_name="Juan Actualizado",
            customer_phone="04161234568",
            customer_national_id="V87654321",
            concept="Concepto nuevo",
        )

        assert transaction.reference == "NEW-REF"
        assert transaction.customer_full_name == "Juan Actualizado"
        mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_transaction_by_id(
        self, service: TransactionService, mock_repo: Mock
    ) -> None:
        """Test getting transaction by ID."""
        transaction_id = uuid4()
        expected_transaction = Transaction(
            id=transaction_id,
            transaction_id="TEST-123",
            status=TransactionStatus.IN_PROGRESS,
            bank=BankType.BANESCO,
            transaction_type=TransactionType.TRANSACTION,
            reference="REF123",
            customer_full_name="Juan Pérez",
            customer_phone="04161234567",
            customer_national_id="V12345678",
            created_at=datetime.utcnow(),
        )

        mock_repo.get_by_id = AsyncMock(return_value=expected_transaction)

        transaction = await service.get_transaction_by_id(transaction_id)

        assert transaction == expected_transaction
        mock_repo.get_by_id.assert_called_once_with(transaction_id)

    @pytest.mark.asyncio
    async def test_list_transactions(
        self, service: TransactionService, mock_repo: Mock
    ) -> None:
        """Test listing transactions with filters."""
        expected_transactions = [
            Transaction(
                id=uuid4(),
                transaction_id=f"TEST-{i}",
                status=TransactionStatus.IN_PROGRESS,
                bank=BankType.BANESCO,
                transaction_type=TransactionType.TRANSACTION,
                reference=f"REF{i}",
                customer_full_name=f"Customer {i}",
                customer_phone="04161234567",
                customer_national_id=f"V1234567{i}",
                created_at=datetime.utcnow(),
            )
            for i in range(3)
        ]

        mock_repo.list_by_filters = AsyncMock(return_value=expected_transactions)

        transactions = await service.list_transactions(
            status=TransactionStatus.IN_PROGRESS,
            skip=0,
            limit=10,
        )

        assert len(transactions) == 3
        assert transactions == expected_transactions
        mock_repo.list_by_filters.assert_called_once()
