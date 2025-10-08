"""Transaction SQLAlchemy models."""

import enum
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class TransactionStatusEnum(str, enum.Enum):
    """Transaction status enumeration."""

    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    UNKNOWN = "UNKNOWN"
    TO_REVIEW = "TO_REVIEW"


class BankTypeEnum(str, enum.Enum):
    """Bank type enumeration."""

    BANESCO = "BANESCO"
    MOBILE_TRANSFER = "MOBILE_TRANSFER"


class TransactionTypeEnum(str, enum.Enum):
    """Transaction type enumeration."""

    TRANSACTION = "TRANSACTION"
    COMMISSION = "COMMISSION"
    OTHER = "OTHER"


class TransactionModel(Base, TimestampMixin, SoftDeleteMixin):
    """Transaction database model."""

    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint(
            "reference", "transaction_type", name="unique_reference_per_type"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    transaction_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    status: Mapped[TransactionStatusEnum] = mapped_column(
        Enum(TransactionStatusEnum, name="transaction_status"),
        nullable=False,
        default=TransactionStatusEnum.IN_PROGRESS,
    )
    bank: Mapped[BankTypeEnum] = mapped_column(
        Enum(BankTypeEnum, name="bank_type"), nullable=False
    )
    transaction_type: Mapped[TransactionTypeEnum] = mapped_column(
        Enum(TransactionTypeEnum, name="transaction_type"),
        nullable=False,
        default=TransactionTypeEnum.TRANSACTION,
    )
    reference: Mapped[str] = mapped_column(String(20), nullable=False)
    customer_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(11), nullable=False)
    customer_national_id: Mapped[str] = mapped_column(String(10), nullable=False)
    concept: Mapped[str | None] = mapped_column(String, nullable=True)
    banesco_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    # Relationships
    creator = relationship(
        "UserModel", back_populates="created_transactions", lazy="select"
    )
    events = relationship(
        "TransactionEventModel", back_populates="transaction", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, transaction_id={self.transaction_id}, status={self.status.value})>"


class ActorTypeEnum(str, enum.Enum):
    """Actor type enumeration."""

    USER = "USER"
    SYSTEM = "SYSTEM"
    EXTERNAL = "EXTERNAL"


class TransactionEventModel(Base, TimestampMixin):
    """Transaction event database model for audit trail."""

    __tablename__ = "transaction_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    transaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False
    )
    old_status: Mapped[TransactionStatusEnum | None] = mapped_column(
        Enum(TransactionStatusEnum, name="transaction_status"), nullable=True
    )
    new_status: Mapped[TransactionStatusEnum] = mapped_column(
        Enum(TransactionStatusEnum, name="transaction_status"), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False, default="USER")
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    transaction = relationship(
        "TransactionModel", back_populates="events", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<TransactionEvent(id={self.id}, transaction_id={self.transaction_id}, {self.old_status} -> {self.new_status})>"
