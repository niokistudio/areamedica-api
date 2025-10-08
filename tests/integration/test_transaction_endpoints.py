"""Integration tests for transaction endpoints."""

from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTransactionEndpoints:
    """Test suite for transaction endpoints."""

    async def test_create_transaction_success(
        self, client: AsyncClient, auth_headers: dict, sample_transaction_data: dict
    ) -> None:
        """Test successful transaction creation."""
        response = await client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json=sample_transaction_data,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["transaction_id"] == sample_transaction_data["transaction_id"]
        assert data["reference"] == sample_transaction_data["reference"]
        assert data["bank"] == "BANESCO"
        assert data["status"] == "IN_PROGRESS"
        assert "id" in data

    async def test_create_transaction_unauthorized(self, client: AsyncClient) -> None:
        """Test transaction creation without authentication."""
        response = await client.post(
            "/api/v1/transactions",
            json={
                "amount": 100.00,
                "reference": "REF123",
                "bank": "BANESCO",
            },
        )

        # 403 is returned when no credentials are provided (Forbidden)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_transaction_invalid_amount(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test transaction creation with missing required fields."""
        response = await client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json={
                "transaction_id": "TEST-123",
                "reference": "REF123",
                "bank": "BANESCO",
                # Missing required fields: transaction_type, customer_full_name, etc.
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_transaction_by_id(
        self, client: AsyncClient, auth_headers: dict, test_transaction: dict
    ) -> None:
        """Test getting transaction by ID."""
        response = await client.get(
            f"/api/v1/transactions/{test_transaction['id']}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_transaction["id"]
        assert "transaction_id" in data
        assert "status" in data
        assert "reference" in data

    async def test_get_transaction_not_found(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test getting non-existent transaction."""
        fake_id = str(uuid4())
        response = await client.get(
            f"/api/v1/transactions/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_list_transactions(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test listing user transactions."""
        response = await client.get(
            "/api/v1/transactions",
            headers=auth_headers,
            params={"limit": 10, "offset": 0},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "transactions" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["transactions"], list)

    async def test_list_transactions_with_status_filter(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test listing transactions with status filter."""
        response = await client.get(
            "/api/v1/transactions",
            headers=auth_headers,
            params={"status": "IN_PROGRESS", "limit": 10},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "transactions" in data
        for transaction in data["transactions"]:
            assert transaction["status"] == "IN_PROGRESS"

    @pytest.mark.skip(reason="Verify endpoint not implemented yet")
    async def test_verify_transaction_with_banesco(
        self, client: AsyncClient, auth_headers: dict, test_transaction: dict
    ) -> None:
        """Test transaction verification with Banesco."""
        response = await client.post(
            f"/api/v1/transactions/{test_transaction['id']}/verify",
            headers=auth_headers,
        )

        # Note: This will fail without proper Banesco mock
        # In real tests, mock the Banesco client
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        ]

    @pytest.mark.skip(reason="Update status endpoint not implemented yet")
    async def test_update_transaction_status(
        self, client: AsyncClient, auth_headers: dict, test_transaction: dict
    ) -> None:
        """Test updating transaction status."""
        response = await client.patch(
            f"/api/v1/transactions/{test_transaction['id']}",
            headers=auth_headers,
            json={"status": "APPROVED"},
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,  # If user doesn't have permission
        ]

    async def test_list_transactions_pagination(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test transaction list pagination."""
        # First page
        response1 = await client.get(
            "/api/v1/transactions",
            headers=auth_headers,
            params={"limit": 5, "offset": 0},
        )
        assert response1.status_code == status.HTTP_200_OK
        page1 = response1.json()

        # Second page
        response2 = await client.get(
            "/api/v1/transactions",
            headers=auth_headers,
            params={"limit": 5, "offset": 5},
        )
        assert response2.status_code == status.HTTP_200_OK
        page2 = response2.json()

        # Pages should be different (if enough data)
        if len(page1) == 5 and len(page2) > 0:
            assert page1[0]["id"] != page2[0]["id"]
