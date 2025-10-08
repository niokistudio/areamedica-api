"""Pytest configuration and fixtures."""

import asyncio
import os
from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.database.models.base import Base
from infrastructure.database.models.transaction import TransactionModel
from infrastructure.database.models.user import UserModel
from interface.api.main import app


# Test database URL - use the development database for tests
TEST_DATABASE_URL = "postgresql+asyncpg://areamedica:password@db:5432/areamedica_dev"

# Set test environment variables
os.environ["SECRET_KEY"] = "test-secret-key"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine for each test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session_factory = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as session:
        yield session
        # Rollback any changes after test
        await session.rollback()


@pytest_asyncio.fixture
async def client(
    test_engine, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden DB dependency."""
    from httpx import ASGITransport

    from infrastructure.database.connection import get_db_session

    # Override the database session dependency
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> dict:
    """Create test user in database."""
    from application.services.auth_service import AuthService

    auth_service = AuthService(
        secret_key="test-secret-key",
        algorithm="HS256",
        access_token_expire_minutes=30,
    )

    password = "TestPassword123!"
    user_id = uuid4()

    user_model = UserModel(
        id=user_id,
        email="testuser@example.com",
        password_hash=auth_service.get_password_hash(password),
        full_name="Test User",
        is_active=True,
    )

    db_session.add(user_model)
    await db_session.commit()  # Use commit so data is available for requests
    await db_session.refresh(user_model)

    # Return dict with password for testing login
    return {
        "id": user_id,
        "email": "testuser@example.com",
        "password": password,
        "full_name": "Test User",
        "is_active": True,
    }


@pytest_asyncio.fixture
async def auth_headers(test_user: dict) -> dict:
    """Create authentication headers with JWT token."""
    from application.services.auth_service import AuthService

    auth_service = AuthService(
        secret_key="test-secret-key",
        algorithm="HS256",
        access_token_expire_minutes=30,
    )

    token = auth_service.create_access_token(
        user_id=test_user["id"],
        email=test_user["email"],
        permissions=[],
    )

    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_transaction(db_session: AsyncSession, test_user: dict) -> dict:
    """Create test transaction in database."""
    transaction_data = {
        "id": uuid4(),
        "transaction_id": "TEST_TRX_123",
        "created_by": test_user["id"],
        "customer_full_name": "Test Customer",
        "customer_phone": "04121234567",
        "customer_national_id": "V12345678",
        "reference": "TEST_REF_123",
        "bank": "BANESCO",
        "status": "IN_PROGRESS",
        "transaction_type": "TRANSACTION",
    }

    transaction_model = TransactionModel(**transaction_data)
    db_session.add(transaction_model)
    await db_session.commit()  # Use commit so data is available for requests
    await db_session.refresh(transaction_model)

    return {**transaction_data, "id": str(transaction_data["id"])}


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing (based on successful endpoint tests)."""
    unique_id = uuid4().hex[:8]
    return {
        "transaction_id": f"TEST-{unique_id}",
        "reference": f"REF-{unique_id}",
        "bank": "BANESCO",
        "transaction_type": "TRANSACTION",
        "customer_full_name": "Juan Pérez",
        "customer_phone": "04161234567",
        "customer_national_id": "V12345678",
        "concept": "Pago de consulta médica",
    }


@pytest.fixture
def sample_user_registration():
    """Sample user registration data for testing."""
    unique_id = uuid4().hex[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    }


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient):
    """Create an authenticated test client with valid token."""
    unique_id = uuid4().hex[:8]
    user_email = f"auth_{unique_id}@example.com"

    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": user_email,
            "password": "TestPassword123!",
            "full_name": "Authenticated Test User",
        },
    )

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_email, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]

    # Create wrapper class to automatically include auth headers
    class AuthenticatedClient:
        def __init__(self, client, token):
            self.client = client
            self.headers = {"Authorization": f"Bearer {token}"}
            self.token = token
            self.email = user_email

        async def post(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return await self.client.post(url, **kwargs)

        async def get(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return await self.client.get(url, **kwargs)

        async def put(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return await self.client.put(url, **kwargs)

        async def delete(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return await self.client.delete(url, **kwargs)

    return AuthenticatedClient(client, token)
