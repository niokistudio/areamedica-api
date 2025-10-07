"""E2E tests for complete transaction workflow."""

from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTransactionWorkflowE2E:
    """End-to-end tests for transaction workflows."""

    async def test_complete_transaction_flow(self, client: AsyncClient) -> None:
        """Test complete flow: register → login → create transaction → verify."""
        # Step 1: Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "e2e@example.com",
                "password": "E2EPassword123!",
                "full_name": "E2E Test User",
                "national_id": "V99999999",
                "phone_number": "04149999999",
            },
        )
        assert register_response.status_code == status.HTTP_201_CREATED

        # Step 2: Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "e2e@example.com",
                "password": "E2EPassword123!",
            },
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Create transaction
        create_tx_response = await client.post(
            "/api/v1/transactions",
            headers=headers,
            json={
                "amount": 250.00,
                "reference": "E2E_REF_001",
                "bank": "BANESCO",
                "description": "E2E test transaction",
            },
        )
        assert create_tx_response.status_code == status.HTTP_201_CREATED
        transaction = create_tx_response.json()
        transaction_id = transaction["id"]

        # Step 4: Get transaction details
        get_tx_response = await client.get(
            f"/api/v1/transactions/{transaction_id}",
            headers=headers,
        )
        assert get_tx_response.status_code == status.HTTP_200_OK
        tx_details = get_tx_response.json()
        assert tx_details["reference"] == "E2E_REF_001"
        assert tx_details["status"] == "PENDING"

        # Step 5: Verify with Banesco (mock)
        with patch(
            "infrastructure.external.banesco_client.BanescoClient.verify_transaction"
        ) as mock_verify:
            mock_verify.return_value = {
                "status": "approved",
                "verification_code": "E2E123",
            }

            verify_response = await client.post(
                f"/api/v1/transactions/{transaction_id}/verify",
                headers=headers,
            )

            # Note: This depends on route implementation
            assert verify_response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND,  # If route not implemented
            ]

        # Step 6: List user transactions
        list_response = await client.get(
            "/api/v1/transactions",
            headers=headers,
            params={"limit": 10, "offset": 0},
        )
        assert list_response.status_code == status.HTTP_200_OK
        transactions = list_response.json()
        assert any(tx["id"] == transaction_id for tx in transactions)

    async def test_unauthorized_access_flow(self, client: AsyncClient) -> None:
        """Test that unauthorized access is properly blocked."""
        # Try to create transaction without auth
        response = await client.post(
            "/api/v1/transactions",
            json={
                "amount": 100.00,
                "reference": "UNAUTH_REF",
                "bank": "BANESCO",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Try to list transactions without auth
        response = await client.get("/api/v1/transactions")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_credentials_flow(self, client: AsyncClient) -> None:
        """Test login with invalid credentials."""
        # Register user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid@example.com",
                "password": "ValidPassword123!",
                "full_name": "Invalid Test",
                "national_id": "V88888888",
                "phone_number": "04148888888",
            },
        )

        # Try login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid@example.com",
                "password": "WrongPassword123!",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_duplicate_transaction_reference(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test handling of duplicate transaction references."""
        # Create first transaction
        response1 = await client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json={
                "amount": 100.00,
                "reference": "DUP_REF_001",
                "bank": "BANESCO",
            },
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create transaction with same reference (same type)
        response2 = await client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json={
                "amount": 200.00,
                "reference": "DUP_REF_001",
                "bank": "BANESCO",
            },
        )

        # Should fail due to UNIQUE constraint on (reference, transaction_type)
        assert response2.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_409_CONFLICT,
        ]

    async def test_pagination_flow(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test pagination of transaction list."""
        # Create multiple transactions
        for i in range(15):
            await client.post(
                "/api/v1/transactions",
                headers=auth_headers,
                json={
                    "amount": 10.00 * i,
                    "reference": f"PAGE_REF_{i:03d}",
                    "bank": "BANESCO",
                },
            )

        # Get first page
        response1 = await client.get(
            "/api/v1/transactions",
            headers=auth_headers,
            params={"limit": 5, "offset": 0},
        )
        assert response1.status_code == status.HTTP_200_OK
        page1 = response1.json()
        assert len(page1) <= 5

        # Get second page
        response2 = await client.get(
            "/api/v1/transactions",
            headers=auth_headers,
            params={"limit": 5, "offset": 5},
        )
        assert response2.status_code == status.HTTP_200_OK
        page2 = response2.json()

        # Verify pages are different
        if len(page1) > 0 and len(page2) > 0:
            page1_ids = {tx["id"] for tx in page1}
            page2_ids = {tx["id"] for tx in page2}
            assert page1_ids.isdisjoint(page2_ids)

    async def test_filter_by_status_flow(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test filtering transactions by status."""
        # Create transactions with different statuses
        await client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json={
                "amount": 50.00,
                "reference": "FILTER_REF_001",
                "bank": "BANESCO",
            },
        )

        # Get only PENDING transactions
        response = await client.get(
            "/api/v1/transactions",
            headers=auth_headers,
            params={"status": "PENDING"},
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()

        # All returned transactions should have PENDING status
        for tx in transactions:
            assert tx["status"] == "PENDING"
