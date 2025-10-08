"""Transaction Data Transfer Objects (DTOs)."""

from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.transaction import BankType, TransactionStatus, TransactionType


class CreateTransactionRequest(BaseModel):
    """Request model for creating a transaction."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    reference: str = Field(..., description="Transaction reference number")
    bank: BankType = Field(..., description="Bank type")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    customer_full_name: str = Field(..., description="Customer full name")
    customer_phone: str = Field(..., description="Customer phone number")
    customer_national_id: str = Field(..., description="Customer national ID")
    concept: str | None = Field(None, description="Transaction concept/description")
    banesco_payload: dict | None = Field(
        None, description="Original Banesco API payload"
    )


class TransactionResponse(BaseModel):
    """Response model for transaction."""

    id: UUID
    transaction_id: str
    reference: str
    bank: BankType
    transaction_type: TransactionType
    status: TransactionStatus
    customer_full_name: str
    customer_phone: str
    customer_national_id: str
    concept: str | None
    extra_data: dict
    created_by: UUID | None
    created_at: str
    updated_at: str

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TransactionListResponse(BaseModel):
    """Response model for transaction list."""

    transactions: list[TransactionResponse]
    total: int
    limit: int
    offset: int
