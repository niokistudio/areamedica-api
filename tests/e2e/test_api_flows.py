"""End-to-End tests for API flows."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthenticationFlow:
    """Test complete authentication flow."""

    async def test_register_login_get_user_flow(self, client: AsyncClient):
        """Test complete user registration and login flow."""
        # Step 1: Register a new user
        user_email = f"e2e_test_{uuid4().hex[:8]}@example.com"
        register_data = {
            "email": user_email,
            "password": "SecurePassword123!",
            "full_name": "E2E Test User",
        }

        register_response = await client.post(
            "/api/v1/auth/register", json=register_data
        )
        assert register_response.status_code == 201
        register_json = register_response.json()
        assert register_json["email"] == user_email
        assert register_json["full_name"] == "E2E Test User"
        assert register_json["is_active"] is True
        user_id = register_json["id"]

        # Step 2: Login with the registered user
        login_data = {"email": user_email, "password": "SecurePassword123!"}

        login_response = await client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        login_json = login_response.json()
        assert "access_token" in login_json
        assert login_json["token_type"] == "bearer"
        token = login_json["access_token"]

        # Step 3: Get current user info with token
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        me_json = me_response.json()
        assert me_json["id"] == user_id
        assert me_json["email"] == user_email
        assert me_json["full_name"] == "E2E Test User"

    async def test_login_with_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials fails."""
        login_data = {"email": "nonexistent@example.com", "password": "WrongPassword"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "detail" in response.json()

    async def test_access_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token fails."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403


@pytest.mark.asyncio
class TestTransactionFlow:
    """Test complete transaction CRUD flow."""

    async def test_complete_transaction_crud_flow(self, client: AsyncClient):
        """Test complete transaction CRUD operations."""
        # Step 1: Register and login to get token
        user_email = f"e2e_txn_{uuid4().hex[:8]}@example.com"
        register_data = {
            "email": user_email,
            "password": "SecurePassword123!",
            "full_name": "Transaction Test User",
        }

        await client.post("/api/v1/auth/register", json=register_data)

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": user_email, "password": "SecurePassword123!"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Create a new transaction
        txn_id = uuid4().hex[:12].upper()
        transaction_data = {
            "transaction_id": f"TXN-E2E-{txn_id}",
            "reference": f"REF-E2E-{txn_id}",
            "bank": "BANESCO",
            "transaction_type": "TRANSACTION",
            "customer_full_name": "Juan Pérez",
            "customer_phone": "04241234567",
            "customer_national_id": "V12345678",
            "concept": "Pago de servicios médicos",
            "banesco_payload": {"amount": "150.00", "currency": "VES"},
        }

        create_response = await client.post(
            "/api/v1/transactions", json=transaction_data, headers=headers
        )
        assert create_response.status_code == 201
        created_txn = create_response.json()
        assert created_txn["transaction_id"] == transaction_data["transaction_id"]
        assert created_txn["reference"] == transaction_data["reference"]
        assert created_txn["status"] == "IN_PROGRESS"
        transaction_uuid = created_txn["id"]

        # Step 3: Get transaction by UUID
        get_by_uuid_response = await client.get(
            f"/api/v1/transactions/{transaction_uuid}", headers=headers
        )
        assert get_by_uuid_response.status_code == 200
        txn_by_uuid = get_by_uuid_response.json()
        assert txn_by_uuid["id"] == transaction_uuid
        assert txn_by_uuid["customer_full_name"] == "Juan Pérez"

        # Step 4: Get transaction by reference
        get_by_ref_response = await client.get(
            f"/api/v1/transactions/reference/{transaction_data['reference']}",
            headers=headers,
        )
        assert get_by_ref_response.status_code == 200
        txn_by_ref = get_by_ref_response.json()
        assert txn_by_ref["id"] == transaction_uuid

        # Step 5: Get transaction by transaction_id
        get_by_txn_id_response = await client.get(
            f"/api/v1/transactions/external/{transaction_data['transaction_id']}",
            headers=headers,
        )
        assert get_by_txn_id_response.status_code == 200
        txn_by_txn_id = get_by_txn_id_response.json()
        assert txn_by_txn_id["id"] == transaction_uuid

        # Step 6: List all transactions
        list_response = await client.get("/api/v1/transactions", headers=headers)
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data["total"] >= 1
        assert len(list_data["transactions"]) >= 1
        assert any(t["id"] == transaction_uuid for t in list_data["transactions"])

        # Step 7: Update transaction (using same transaction_id)
        updated_data = {
            **transaction_data,
            "customer_full_name": "Juan Pérez ACTUALIZADO",
            "concept": "Pago de servicios médicos - ACTUALIZADO",
        }

        update_response = await client.post(
            "/api/v1/transactions", json=updated_data, headers=headers
        )
        assert update_response.status_code == 201
        updated_txn = update_response.json()
        assert updated_txn["id"] == transaction_uuid  # Same UUID
        assert updated_txn["customer_full_name"] == "Juan Pérez ACTUALIZADO"
        assert "ACTUALIZADO" in updated_txn["concept"]

        # Step 8: Verify update persisted
        verify_response = await client.get(
            f"/api/v1/transactions/{transaction_uuid}", headers=headers
        )
        assert verify_response.status_code == 200
        verified_txn = verify_response.json()
        assert verified_txn["customer_full_name"] == "Juan Pérez ACTUALIZADO"
        assert "ACTUALIZADO" in verified_txn["concept"]

    async def test_list_transactions_with_filters(self, client: AsyncClient):
        """Test listing transactions with filters and pagination."""
        # Register and login
        user_email = f"e2e_filter_{uuid4().hex[:8]}@example.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": user_email,
                "password": "SecurePassword123!",
                "full_name": "Filter Test User",
            },
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": user_email, "password": "SecurePassword123!"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create multiple transactions
        for i in range(3):
            await client.post(
                "/api/v1/transactions",
                json={
                    "transaction_id": f"TXN-FILTER-{i}",
                    "reference": f"REF-FILTER-{i}",
                    "bank": "BANESCO",
                    "transaction_type": "TRANSACTION",
                    "customer_full_name": f"Cliente {i}",
                    "customer_phone": "04241234567",
                    "customer_national_id": "V12345678",
                    "concept": "Test",
                },
                headers=headers,
            )

        # Test pagination with limit
        limit_response = await client.get(
            "/api/v1/transactions?limit=2", headers=headers
        )
        assert limit_response.status_code == 200
        limit_data = limit_response.json()
        assert len(limit_data["transactions"]) <= 2
        assert limit_data["limit"] == 2

        # Test with offset
        offset_response = await client.get(
            "/api/v1/transactions?limit=2&offset=1", headers=headers
        )
        assert offset_response.status_code == 200
        offset_data = offset_response.json()
        assert offset_data["offset"] == 1

    async def test_transaction_not_found(self, client: AsyncClient):
        """Test getting non-existent transaction returns 404."""
        # Register and login
        user_email = f"e2e_notfound_{uuid4().hex[:8]}@example.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": user_email,
                "password": "SecurePassword123!",
                "full_name": "NotFound Test User",
            },
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": user_email, "password": "SecurePassword123!"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to get non-existent transaction
        response = await client.get(
            "/api/v1/transactions/reference/NONEXISTENT", headers=headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check endpoints."""

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "areamedica-api"

    async def test_readiness_check(self, client: AsyncClient):
        """Test readiness check endpoint."""
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "areamedica-api"

    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
