"""Transaction domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


class TransactionStatus(str, Enum):
    """Transaction status enumeration."""

    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    UNKNOWN = "UNKNOWN"
    TO_REVIEW = "TO_REVIEW"


class BankType(str, Enum):
    """Bank type enumeration."""

    BANESCO = "BANESCO"
    MOBILE_TRANSFER = "MOBILE_TRANSFER"


class TransactionType(str, Enum):
    """Transaction type enumeration."""

    TRANSACTION = "TRANSACTION"
    COMMISSION = "COMMISSION"
    OTHER = "OTHER"


@dataclass
class Transaction:
    """Transaction entity."""

    id: UUID
    transaction_id: str
    status: TransactionStatus
    bank: BankType
    transaction_type: TransactionType
    reference: str
    customer_full_name: str
    customer_phone: str
    customer_national_id: str
    concept: str | None = None
    banesco_payload: dict | None = None
    extra_data: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
    created_by: UUID | None = None

    def is_completed(self) -> bool:
        """Check if transaction is completed."""
        return self.status == TransactionStatus.COMPLETED

    def is_in_progress(self) -> bool:
        """Check if transaction is in progress."""
        return self.status == TransactionStatus.IN_PROGRESS

    def is_deleted(self) -> bool:
        """Check if transaction is soft-deleted."""
        return self.deleted_at is not None

    def __str__(self) -> str:
        return f"Transaction {self.transaction_id} - {self.status.value}"
