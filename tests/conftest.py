"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.database.models.base import Base
from infrastructure.database.models.user import UserModel
from interface.api.main import app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.database.models.base import Base
from infrastructure.database.models.user import UserModel
from infrastructure.database.models.transaction import TransactionModel
from interface.api.main import app


# Test database URL - use a separate test database
TEST_DATABASE_URL = (
    "postgresql+asyncpg://areamedica:password@localhost:5432/areamedica_test"
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.fixture
async def test_user(db_session: AsyncSession) -> dict:
    """Create test user in database."""
    from uuid import uuid4

    from application.services.auth_service import AuthService

    auth_service = AuthService(
        secret_key="test-secret-key",
        algorithm="HS256",
        access_token_expire_minutes=30,
    )

    user_data = {
        "id": uuid4(),
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "password_hash": auth_service.get_password_hash("TestPassword123!"),
        "full_name": "Test User",
        "national_id": "V12345678",
        "phone_number": "04121234567",
        "is_active": True,
    }

    user_model = UserModel(
        id=user_data["id"],
        email=user_data["email"],
        password_hash=user_data["password_hash"],
        full_name=user_data["full_name"],
        national_id=user_data["national_id"],
        phone_number=user_data["phone_number"],
        is_active=user_data["is_active"],
    )

    db_session.add(user_model)
    await db_session.commit()

    return user_data


@pytest.fixture
def auth_headers(test_user: dict) -> dict:
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


@pytest.fixture
async def test_transaction(db_session: AsyncSession, test_user: dict) -> dict:
    """Create test transaction in database."""
    from decimal import Decimal
    from uuid import uuid4

    transaction_data = {
        "id": uuid4(),
        "user_id": test_user["id"],
        "amount": Decimal("100.50"),
        "reference": "TEST_REF_123",
        "bank": "BANESCO",
        "status": "PENDING",
        "transaction_type": "TRANSACTION",
    }

    transaction_model = TransactionModel(**transaction_data)
    db_session.add(transaction_model)
    await db_session.commit()

    return {**transaction_data, "id": str(transaction_data["id"])}


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "transaction_id": "TEST123456789",
        "customer": {
            "full_name": "Juan Pérez",
            "phone": "04161234567",
            "national_id": "V12345678",
            "concept": "Pago de consulta médica",
        },
        "reference": "123456789",
        "bank": "BANESCO",
    }
