"""add_seed_data_for_testing

Revision ID: 42be14e03be4
Revises: eceff2145126
Create Date: 2025-10-12 18:22:38.598269

"""

from typing import Sequence, Union
from uuid import uuid4
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import bcrypt


# revision identifiers, used by Alembic.
revision: str = "42be14e03be4"
down_revision: Union[str, None] = "eceff2145126"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def upgrade() -> None:
    """Add seed data for testing."""

    # Define tables
    users_table = table(
        "users",
        column("id", UUID(as_uuid=True)),
        column("email", String),
        column("password_hash", String),
        column("full_name", String),
        column("is_active", Boolean),
        column("created_at", DateTime),
        column("updated_at", DateTime),
    )

    transactions_table = table(
        "transactions",
        column("id", UUID(as_uuid=True)),
        column("transaction_id", String),
        column("reference", String),
        column("bank", sa.Enum("BANESCO", "MOBILE_TRANSFER", name="bank_type")),
        column(
            "transaction_type",
            sa.Enum("TRANSACTION", "COMMISSION", "OTHER", name="transaction_type"),
        ),
        column(
            "status",
            sa.Enum(
                "IN_PROGRESS",
                "WAITING_APPROVAL",
                "APPROVED",
                "COMPLETED",
                "REJECTED",
                "CANCELLED",
                "TO_REVIEW",
                "REVIEWED",
                name="transaction_status",
            ),
        ),
        column("customer_full_name", String),
        column("customer_phone", String),
        column("customer_national_id", String),
        column("concept", String),
        column("extra_data", JSONB),
        column("created_by", UUID(as_uuid=True)),
        column("created_at", DateTime),
        column("updated_at", DateTime),
    )

    # Create test users
    admin_user_id = uuid4()
    regular_user_id = uuid4()
    test_user_id = uuid4()

    now = datetime.now()

    # Password: Admin123!
    admin_password_hash = hash_password("Admin123!")
    # Password: User123!
    user_password_hash = hash_password("User123!")
    # Password: Test123!
    test_password_hash = hash_password("Test123!")

    users_data = [
        {
            "id": admin_user_id,
            "email": "admin@areamedica.com",
            "password_hash": admin_password_hash,
            "full_name": "Administrador Sistema",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": regular_user_id,
            "email": "usuario@areamedica.com",
            "password_hash": user_password_hash,
            "full_name": "Usuario Regular",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": test_user_id,
            "email": "test@areamedica.com",
            "password_hash": test_password_hash,
            "full_name": "Usuario de Prueba",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
    ]

    # Create test transactions
    transactions_data = [
        {
            "id": uuid4(),
            "transaction_id": "TRX-2025-001",
            "reference": "REF-BANESCO-001",
            "bank": "BANESCO",
            "transaction_type": "TRANSACTION",
            "status": "IN_PROGRESS",
            "customer_full_name": "Juan Pérez García",
            "customer_phone": "04121234567",
            "customer_national_id": "V12345678",
            "concept": "Consulta médica general",
            "extra_data": {},
            "created_by": admin_user_id,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid4(),
            "transaction_id": "TRX-2025-002",
            "reference": "REF-BANESCO-002",
            "bank": "BANESCO",
            "transaction_type": "TRANSACTION",
            "status": "COMPLETED",
            "customer_full_name": "María González López",
            "customer_phone": "04149876543",
            "customer_national_id": "V23456789",
            "concept": "Laboratorio clínico",
            "extra_data": {},
            "created_by": admin_user_id,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid4(),
            "transaction_id": "TRX-2025-003",
            "reference": "REF-BANESCO-003",
            "bank": "BANESCO",
            "transaction_type": "TRANSACTION",
            "status": "IN_PROGRESS",
            "customer_full_name": "Carlos Rodríguez Martínez",
            "customer_phone": "04161112233",
            "customer_national_id": "V34567890",
            "concept": "Radiografía torácica",
            "extra_data": {},
            "created_by": regular_user_id,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid4(),
            "transaction_id": "TRX-2025-004",
            "reference": "REF-BANESCO-004",
            "bank": "BANESCO",
            "transaction_type": "COMMISSION",
            "status": "COMPLETED",
            "customer_full_name": "Ana Fernández Silva",
            "customer_phone": "04124445566",
            "customer_national_id": "V45678901",
            "concept": "Comisión por servicio",
            "extra_data": {},
            "created_by": regular_user_id,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid4(),
            "transaction_id": "TRX-2025-005",
            "reference": "REF-MOBILE-001",
            "bank": "MOBILE_TRANSFER",
            "transaction_type": "TRANSACTION",
            "status": "TO_REVIEW",
            "customer_full_name": "Luis Morales Castro",
            "customer_phone": "04167778899",
            "customer_national_id": "V56789012",
            "concept": "Pago móvil por consulta",
            "extra_data": {},
            "created_by": test_user_id,
            "created_at": now,
            "updated_at": now,
        },
    ]

    # Insert data
    op.bulk_insert(users_table, users_data)
    op.bulk_insert(transactions_table, transactions_data)


def downgrade() -> None:
    """Remove seed data."""
    # Delete test data in reverse order (due to foreign keys)
    op.execute("DELETE FROM transactions WHERE transaction_id LIKE 'TRX-2025-%'")
    op.execute(
        "DELETE FROM users WHERE email IN ('admin@areamedica.com', 'usuario@areamedica.com', 'test@areamedica.com')"
    )
