"""Transaction API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.transaction_dto import (
    CreateTransactionRequest,
    TransactionListResponse,
    TransactionResponse,
)
from application.services.transaction_service import TransactionService
from domain.entities.transaction import BankType, TransactionStatus, TransactionType
from domain.entities.user import User
from infrastructure.database.connection import get_db_session
from infrastructure.database.repositories.transaction_repository import (
    TransactionRepository,
)
from interface.api.routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


def get_transaction_service(
    session: AsyncSession = Depends(get_db_session),
) -> TransactionService:
    """Dependency to get transaction service."""
    transaction_repo = TransactionRepository(session)
    return TransactionService(transaction_repo=transaction_repo)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update a transaction",
    description="Creates a new transaction or updates an existing one based on transaction_id",
)
async def create_transaction(
    request: CreateTransactionRequest,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    """
    Create or update a transaction.

    If a transaction with the same transaction_id exists, it will be updated.
    Otherwise, a new transaction will be created.
    """
    try:
        transaction = await service.create_or_update_transaction(
            transaction_id=request.transaction_id,
            reference=request.reference,
            bank=request.bank,
            transaction_type=request.transaction_type,
            customer_full_name=request.customer_full_name,
            customer_phone=request.customer_phone,
            customer_national_id=request.customer_national_id,
            concept=request.concept,
            banesco_payload=request.banesco_payload,
            created_by=current_user.id,
        )

        return TransactionResponse(
            id=transaction.id,
            transaction_id=transaction.transaction_id,
            reference=transaction.reference,
            bank=transaction.bank,
            transaction_type=transaction.transaction_type,
            status=transaction.status,
            customer_full_name=transaction.customer_full_name,
            customer_phone=transaction.customer_phone,
            customer_national_id=transaction.customer_national_id,
            concept=transaction.concept,
            extra_data=transaction.extra_data,
            created_by=transaction.created_by,
            created_at=transaction.created_at.isoformat(),
            updated_at=transaction.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating transaction: {str(e)}",
        ) from e


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction by ID",
    description="Retrieve a specific transaction by its UUID",
)
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    """Get a specific transaction by ID."""
    transaction = await service.get_transaction_by_id(transaction_id)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )

    return TransactionResponse(
        id=transaction.id,
        transaction_id=transaction.transaction_id,
        reference=transaction.reference,
        bank=transaction.bank,
        transaction_type=transaction.transaction_type,
        status=transaction.status,
        customer_full_name=transaction.customer_full_name,
        customer_phone=transaction.customer_phone,
        customer_national_id=transaction.customer_national_id,
        concept=transaction.concept,
        extra_data=transaction.extra_data,
        created_by=transaction.created_by,
        created_at=transaction.created_at.isoformat(),
        updated_at=transaction.updated_at.isoformat(),
    )


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List transactions",
    description="List transactions with optional filters and pagination",
)
async def list_transactions(
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
    status_filter: TransactionStatus | None = Query(
        None, description="Filter by transaction status"
    ),
    bank_filter: BankType | None = Query(None, description="Filter by bank type"),
    transaction_type_filter: TransactionType | None = Query(
        None, description="Filter by transaction type"
    ),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
) -> TransactionListResponse:
    """
    List transactions with filters and pagination.

    Supports filtering by:
    - Status (IN_PROGRESS, COMPLETED, CANCELED, etc.)
    - Bank (BANESCO, MOBILE_TRANSFER)
    - Transaction Type

    Pagination:
    - limit: Max results per page (1-100, default 50)
    - offset: Number of results to skip (default 0)
    """
    transactions, total = await service.list_transactions(
        status=status_filter,
        bank=bank_filter,
        transaction_type=transaction_type_filter,
        limit=limit,
        offset=offset,
    )

    return TransactionListResponse(
        transactions=[
            TransactionResponse(
                id=t.id,
                transaction_id=t.transaction_id,
                reference=t.reference,
                bank=t.bank,
                transaction_type=t.transaction_type,
                status=t.status,
                customer_full_name=t.customer_full_name,
                customer_phone=t.customer_phone,
                customer_national_id=t.customer_national_id,
                concept=t.concept,
                extra_data=t.extra_data,
                created_by=t.created_by,
                created_at=t.created_at.isoformat(),
                updated_at=t.updated_at.isoformat(),
            )
            for t in transactions
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/reference/{reference}",
    response_model=TransactionResponse,
    summary="Get transaction by reference",
    description="Retrieve a specific transaction by its reference number",
)
async def get_transaction_by_reference(
    reference: str,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    """Get a specific transaction by reference number."""
    transaction = await service.get_transaction_by_reference(reference)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with reference {reference} not found",
        )

    return TransactionResponse(
        id=transaction.id,
        transaction_id=transaction.transaction_id,
        reference=transaction.reference,
        bank=transaction.bank,
        transaction_type=transaction.transaction_type,
        status=transaction.status,
        customer_full_name=transaction.customer_full_name,
        customer_phone=transaction.customer_phone,
        customer_national_id=transaction.customer_national_id,
        concept=transaction.concept,
        extra_data=transaction.extra_data,
        created_by=transaction.created_by,
        created_at=transaction.created_at.isoformat(),
        updated_at=transaction.updated_at.isoformat(),
    )


@router.get(
    "/external/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction by external transaction ID",
    description="Retrieve a specific transaction by its external transaction_id",
)
async def get_transaction_by_transaction_id(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    """Get a specific transaction by external transaction_id."""
    transaction = await service.get_transaction_by_transaction_id(transaction_id)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with transaction_id {transaction_id} not found",
        )

    return TransactionResponse(
        id=transaction.id,
        transaction_id=transaction.transaction_id,
        reference=transaction.reference,
        bank=transaction.bank,
        transaction_type=transaction.transaction_type,
        status=transaction.status,
        customer_full_name=transaction.customer_full_name,
        customer_phone=transaction.customer_phone,
        customer_national_id=transaction.customer_national_id,
        concept=transaction.concept,
        extra_data=transaction.extra_data,
        created_by=transaction.created_by,
        created_at=transaction.created_at.isoformat(),
        updated_at=transaction.updated_at.isoformat(),
    )
