"""Unit tests for TransactionService."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from application.services.transaction_service import TransactionService
from domain.entities.transaction import BankType, Transaction, TransactionStatus


class TestTransactionService:
    """Test suite for TransactionService."""

    @pytest.fixture
    def mock_repo(self) -> Mock:
        """Create mock transaction repository."""
        return Mock()

    @pytest.fixture
    def mock_banesco_client(self) -> Mock:
        """Create mock Banesco client."""
        return Mock()

    @pytest.fixture
    def service(self, mock_repo: Mock, mock_banesco_client: Mock) -> TransactionService:
        """Create TransactionService instance."""
        return TransactionService(
            repository=mock_repo, banesco_client=mock_banesco_client
        )

    @pytest.mark.asyncio
    async def test_create_transaction(
        self, service: TransactionService, mock_repo: Mock
    ) -> None:
        """Test transaction creation."""
        user_id = uuid4()
        mock_repo.create = AsyncMock(
            return_value=Transaction(
                id=uuid4(),
                user_id=user_id,
                amount=Decimal("100.50"),
                reference="REF123",
                bank=BankType.BANESCO,
                status=TransactionStatus.PENDING,
                transaction_type="TRANSACTION",
                created_at=datetime.utcnow(),
            )
        )

        transaction = await service.create_transaction(
            user_id=user_id,
            amount=Decimal("100.50"),
            reference="REF123",
            bank=BankType.BANESCO,
        )

        assert transaction.user_id == user_id
        assert transaction.amount == Decimal("100.50")
        assert transaction.status == TransactionStatus.PENDING
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_with_banesco_success(
        self, service: TransactionService, mock_banesco_client: Mock, mock_repo: Mock
    ) -> None:
        """Test successful Banesco verification."""
        transaction_id = uuid4()
        mock_transaction = Transaction(
            id=transaction_id,
            user_id=uuid4(),
            amount=Decimal("100.00"),
            reference="REF123",
            bank=BankType.BANESCO,
            status=TransactionStatus.PENDING,
            transaction_type="TRANSACTION",
            created_at=datetime.utcnow(),
        )

        mock_repo.get_by_id = AsyncMock(return_value=mock_transaction)
        mock_banesco_client.verify_transaction = AsyncMock(
            return_value={"status": "approved", "verification_code": "ABC123"}
        )
        mock_repo.update = AsyncMock()

        result = await service.verify_with_banesco(transaction_id)

        assert result["status"] == "approved"
        mock_banesco_client.verify_transaction.assert_called_once_with("REF123")
        mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_transaction_not_found(
        self, service: TransactionService, mock_repo: Mock
    ) -> None:
        """Test verification when transaction not found."""
        mock_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Transaction not found"):
            await service.verify_with_banesco(uuid4())

    @pytest.mark.asyncio
    async def test_list_transactions_with_filters(
        self, service: TransactionService, mock_repo: Mock
    ) -> None:
        """Test listing transactions with filters."""
        user_id = uuid4()
        mock_transactions = [
            Transaction(
                id=uuid4(),
                user_id=user_id,
                amount=Decimal("50.00"),
                reference=f"REF{i}",
                bank=BankType.BANESCO,
                status=TransactionStatus.APPROVED,
                transaction_type="TRANSACTION",
                created_at=datetime.utcnow(),
            )
            for i in range(3)
        ]

        mock_repo.list_by_user = AsyncMock(return_value=mock_transactions)

        transactions = await service.list_transactions(
            user_id=user_id,
            status=TransactionStatus.APPROVED,
            limit=10,
            offset=0,
        )

        assert len(transactions) == 3
        mock_repo.list_by_user.assert_called_once_with(
            user_id=user_id,
            status=TransactionStatus.APPROVED,
            limit=10,
            offset=0,
        )
