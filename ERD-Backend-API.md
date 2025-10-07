# Engineering Requirements Document (ERD)
## Área Médica Backend API - Banking Transaction Management System

### Version: 1.0
### Date: September 30, 2025
### Status: In Progress
### Overall Progress: 🚀 **45%**

---

## 📊 Implementation Progress Summary

| Section                           | Status        | Progress |
| --------------------------------- | ------------- | -------- |
| 1. Architecture Overview          | ✅ Complete    | 100%     |
| 2. Technology Stack               | ✅ Complete    | 100%     |
| 3. Project Structure              | ✅ Complete    | 100%     |
| 4. Database Design                | 🚧 In Progress | 10%      |
| 5. API Specifications             | 🚧 In Progress | 15%      |
| 6. Authentication & Authorization | ⏳ Not Started | 0%       |
| 7. Banking Integration (Banesco)  | ⏳ Not Started | 0%       |
| 8. Infrastructure & Deployment    | 🚧 In Progress | 60%      |
| 9. Development Environment        | ✅ Complete    | 100%     |
| 10. CI/CD Pipeline                | ⏳ Not Started | 0%       |
| 11. Monitoring & Observability    | 🚧 In Progress | 30%      |
| 12. Code Quality & Standards      | ✅ Complete    | 100%     |
| 13. Security Requirements         | ⏳ Not Started | 0%       |
| 14. Performance Requirements      | ⏳ Not Started | 0%       |
| 15. Testing Strategy              | 🚧 In Progress | 20%      |
| 16. Environment Configuration     | ✅ Complete    | 100%     |
| 17. Additional Considerations     | ⏳ Not Started | 0%       |

**Legend:**
- ✅ Complete (100%)
- 🚧 In Progress (1-99%)
- ⏳ Not Started (0%)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Database Design](#4-database-design)
5. [API Specifications](#5-api-specifications)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [Banking Integration (Banesco)](#7-banking-integration-banesco)
8. [Infrastructure & Deployment](#8-infrastructure--deployment)
9. [Development Environment](#9-development-environment)
10. [CI/CD Pipeline](#10-cicd-pipeline)
11. [Monitoring & Observability](#11-monitoring--observability)
12. [Code Quality & Standards](#12-code-quality--standards)
13. [Security Requirements](#13-security-requirements)
14. [Performance Requirements](#14-performance-requirements)
15. [Testing Strategy](#15-testing-strategy)
16. [Environment Configuration](#16-environment-configuration)
17. [Additional Considerations](#17-additional-considerations)

---

## 1. Architecture Overview ✅ 100%

### 1.1 Clean Architecture Layers

The backend will follow Clean Architecture principles with the following layers:

```
src/
├── domain/           # Core business logic, entities, value objects
├── application/      # Use cases, application services, DTOs
├── infrastructure/   # External dependencies, database, APIs
└── interface/        # Controllers, FastAPI routes, middleware
```

### 1.2 Design Patterns

- **Repository Pattern**: Data access abstraction
- **Unit of Work**: Transaction management
- **Factory Pattern**: Object creation
- **Strategy Pattern**: Payment processing strategies
- **Command Query Responsibility Segregation (CQRS)**: Separate read/write operations

### 1.3 Core Components

- **Transaction Management Service**: Handle banking transactions
- **Banking Gateway**: Banesco API integration
- **Authentication Service**: User management and permissions
- **Rate Limiting Service**: API rate control
- **Audit Service**: Transaction event logging

---

## 2. Technology Stack ✅ 100%

### 2.1 Core Framework
- **FastAPI**: High-performance async web framework
- **Pydantic v2**: Data validation and serialization
- **Python 3.11+**: Latest stable Python version

### 2.2 Database
- **PostgreSQL 15+**: Primary database
- **SQLAlchemy 2.0+**: ORM with async support
- **Alembic**: Database migrations

### 2.3 Additional Libraries
```python
# Core Dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0.post1
pydantic==2.5.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.13.0

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# HTTP Client & Banking Integration
httpx==0.25.1
tenacity==8.2.3

# Monitoring & Logging
prometheus-client==0.19.0
structlog==23.2.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0

# Development & Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
ruff==0.1.6  # Linting and formatting
```

---

## 3. Project Structure ✅ 100%

```
areamedica-api/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── docker/
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── docker-compose.yml
├── docs/
│   ├── api/
│   └── deployment/
├── infrastructure/
│   ├── terraform/
│   └── kubernetes/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py
│   │   │   ├── user.py
│   │   │   └── permission.py
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   ├── transaction_id.py
│   │   │   ├── phone_number.py
│   │   │   └── national_id.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── transaction_repository.py
│   │   │   └── user_repository.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── domain_services.py
│   ├── application/
│   │   ├── dto/
│   │   │   ├── __init__.py
│   │   │   ├── transaction_dto.py
│   │   │   └── auth_dto.py
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── create_transaction.py
│   │   │   └── get_transaction_status.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── transaction_service.py
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   ├── models/
│   │   │   └── repositories/
│   │   ├── external/
│   │   │   ├── __init__.py
│   │   │   └── banesco_client.py
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   └── redis_cache.py
│   │   └── monitoring/
│   │       ├── __init__.py
│   │       ├── metrics.py
│   │       └── logging.py
│   └── interface/
│       ├── api/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── transactions.py
│       │   │   ├── auth.py
│       │   │   └── health.py
│       │   └── middleware/
│       │       ├── __init__.py
│       │       ├── auth_middleware.py
│       │       ├── rate_limit_middleware.py
│       │       └── logging_middleware.py
│       └── cli/
│           ├── __init__.py
│           └── commands.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── migrations/
├── scripts/
├── .env.example
├── .gitignore
├── Makefile
├── pyproject.toml
├── README.md
└── requirements/
    ├── base.txt
    ├── dev.txt
    └── prod.txt
```

---

## 4. Database Design 🚧 10%

### 4.1 Database Schema

```sql
-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_permissions (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    PRIMARY KEY (user_id, permission_id)
);

-- Transactions
CREATE TYPE transaction_status AS ENUM (
    'IN_PROGRESS',
    'COMPLETED', 
    'CANCELED',
    'UNKNOWN',
    'TO_REVIEW'
);

CREATE TYPE bank_type AS ENUM (
    'BANESCO',
    'MOBILE_TRANSFER'
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    status transaction_status NOT NULL DEFAULT 'IN_PROGRESS',
    bank bank_type NOT NULL,
    reference VARCHAR(20) NOT NULL,
    customer_full_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(11) NOT NULL,
    customer_national_id VARCHAR(10) NOT NULL,
    concept TEXT,
    banesco_payload JSONB,
    metadata JSONB DEFAULT '{}',  -- Optional
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    created_by UUID REFERENCES users(id)
);

-- Transaction Events (Audit Trail)
CREATE TABLE transaction_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    old_status transaction_status,
    new_status transaction_status NOT NULL,
    reason TEXT,
    actor_type VARCHAR(20) DEFAULT 'USER', -- USER, SYSTEM, EXTERNAL
    actor_id UUID REFERENCES users(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Rate Limiting
CREATE TABLE rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_type VARCHAR(50) NOT NULL, -- 'TRANSACTION_ID', 'IP', 'USER'
    resource_identifier VARCHAR(255) NOT NULL,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    request_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(resource_type, resource_identifier, window_start)
);

-- Indexes
CREATE INDEX idx_transactions_transaction_id ON transactions(transaction_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_created_at_status ON transactions(created_at, status);
CREATE INDEX idx_transactions_reference ON transactions(reference);
CREATE INDEX idx_transactions_customer_phone ON transactions(customer_phone);
CREATE INDEX idx_transactions_customer_national_id ON transactions(customer_national_id);
CREATE INDEX idx_transaction_events_transaction_id ON transaction_events(transaction_id);
CREATE INDEX idx_transaction_events_created_at ON transaction_events(created_at);
CREATE INDEX idx_rate_limits_resource ON rate_limits(resource_type, resource_identifier);
CREATE INDEX idx_rate_limits_window_start ON rate_limits(window_start);
```

### 4.2 Database Configuration

```python
# src/infrastructure/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
)

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)
```

---

## 5. API Specifications 🚧 15%

### 5.1 API Structure

```python
# src/interface/api/routes/transactions.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from application.dto.transaction_dto import (
    CreateTransactionRequest,
    TransactionResponse,
    TransactionListResponse,
    TransactionStatusResponse
)

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    request: CreateTransactionRequest,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends()
):
    """Create or update a transaction."""
    pass

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends()
):
    """Get transaction details."""
    pass

@router.get("/{transaction_id}/status", response_model=TransactionStatusResponse)
async def get_transaction_status(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends()
):
    """Get current transaction status with Banesco sync if needed."""
    pass

@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    page: int = 1,
    size: int = 20,
    status: Optional[str] = None,
    reference: Optional[str] = None,
    phone: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends()
):
    """List transactions with filtering and pagination."""
    pass
```

### 5.2 Data Transfer Objects

```python
# src/application/dto/transaction_dto.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class BankType(str, Enum):
    BANESCO = "BANESCO"
    MOBILE_TRANSFER = "MOBILE_TRANSFER"

class TransactionStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    UNKNOWN = "UNKNOWN"
    TO_REVIEW = "TO_REVIEW"

class CustomerData(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., regex=r'^\d{11}$')
    national_id: str = Field(..., regex=r'^V\d{4,8}$')
    concept: Optional[str] = Field(None, max_length=500)

    @validator('full_name')
    def validate_full_name(cls, v):
        if not v.replace(' ', '').isalpha():
            raise ValueError('Full name must contain only alphabetic characters')
        return v.title()

class CreateTransactionRequest(BaseModel):
    transaction_id: str = Field(..., min_length=1, max_length=100)
    customer: CustomerData
    reference: str = Field(..., regex=r'^\d{9}$')
    bank: BankType

class TransactionResponse(BaseModel):
    id: str
    transaction_id: str
    status: TransactionStatus
    bank: BankType
    reference: str
    customer: CustomerData
    created_at: datetime
    updated_at: datetime
    banesco_details: Optional[dict] = None

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    size: int
    pages: int
```

---

## 6. Authentication & Authorization ⏳ 0%

### 6.1 JWT Authentication

```python
# src/application/services/auth_service.py
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

### 6.2 Permission System

```python
# src/domain/entities/permission.py
from dataclasses import dataclass
from typing import List
from enum import Enum

class PermissionType(str, Enum):
    TRANSACTION_CREATE = "transaction:create"
    TRANSACTION_READ = "transaction:read"
    TRANSACTION_UPDATE = "transaction:update"
    TRANSACTION_DELETE = "transaction:delete"
    ADMIN_ACCESS = "admin:access"

@dataclass
class Permission:
    id: str
    name: PermissionType
    description: str

@dataclass
class User:
    id: str
    email: str
    full_name: str
    is_active: bool
    permissions: List[Permission]

    def has_permission(self, permission: PermissionType) -> bool:
        return any(p.name == permission for p in self.permissions)
```

---

## 7. Banking Integration (Banesco) ⏳ 0%

### 7.1 Banesco Client

```python
# src/infrastructure/external/banesco_client.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger()

class BanescoClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={"Authorization": f"Bearer {api_key}"}
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_transaction_status(
        self, 
        transaction_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get transaction status from Banesco API."""
        try:
            response = await self.client.get(
                f"{self.base_url}/transactions/{transaction_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(
                    "Transaction not found in Banesco", 
                    transaction_id=transaction_id
                )
                return None
            elif response.status_code == 429:
                logger.warning(
                    "Rate limited by Banesco", 
                    transaction_id=transaction_id
                )
                raise BanescoRateLimitError()
            else:
                response.raise_for_status()
                
        except httpx.TimeoutException:
            logger.error(
                "Banesco API timeout", 
                transaction_id=transaction_id
            )
            raise BanescoTimeoutError()
        except Exception as e:
            logger.error(
                "Banesco API error", 
                transaction_id=transaction_id, 
                error=str(e)
            )
            raise BanescoAPIError(str(e))

    async def close(self):
        await self.client.aclose()

class BanescoAPIError(Exception):
    pass

class BanescoTimeoutError(BanescoAPIError):
    pass

class BanescoRateLimitError(BanescoAPIError):
    pass
```

### 7.2 Rate Limiting Service

```python
# src/application/services/rate_limit_service.py
from datetime import datetime, timedelta
from infrastructure.database.repositories.rate_limit_repository import RateLimitRepository

class RateLimitService:
    def __init__(self, rate_limit_repo: RateLimitRepository):
        self.rate_limit_repo = rate_limit_repo
        self.banesco_rate_limit = 2  # 2 requests per minute per transaction_id

    async def check_rate_limit(
        self, 
        resource_type: str, 
        resource_id: str
    ) -> bool:
        """Check if request is within rate limit."""
        now = datetime.utcnow()
        window_start = now.replace(second=0, microsecond=0)
        
        current_count = await self.rate_limit_repo.get_request_count(
            resource_type, resource_id, window_start
        )
        
        if resource_type == "TRANSACTION_ID":
            return current_count < self.banesco_rate_limit
        
        return True

    async def increment_rate_limit(
        self, 
        resource_type: str, 
        resource_id: str
    ):
        """Increment rate limit counter."""
        now = datetime.utcnow()
        window_start = now.replace(second=0, microsecond=0)
        
        await self.rate_limit_repo.increment_count(
            resource_type, resource_id, window_start
        )
```

---

## 8. Infrastructure & Deployment 🚧 60%

### 8.1 Docker Configuration

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

# Copy application code
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

CMD ["uvicorn", "src.interface.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/areamedica
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./src:/app/src
      - ./migrations:/app/migrations

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: areamedica
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  grafana_data:
```

### 8.2 Infrastructure as Code (Terraform)

```hcl
# infrastructure/terraform/main.tf
terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "api_server" {
  image  = "ubuntu-22-04-x64"
  name   = "areamedica-api"
  region = "nyc3"
  size   = "s-2vcpu-2gb"
  
  ssh_keys = [var.ssh_key_fingerprint]
  
  user_data = file("${path.module}/cloud-init.yml")
  
  tags = ["api", "production"]
}

resource "digitalocean_database_cluster" "postgres" {
  name       = "areamedica-db"
  engine     = "pg"
  version    = "15"
  size       = "db-s-1vcpu-1gb"
  region     = "nyc3"
  node_count = 1
  
  tags = ["database", "production"]
}

resource "digitalocean_loadbalancer" "api_lb" {
  name   = "areamedica-lb"
  region = "nyc3"
  
  forwarding_rule {
    entry_protocol  = "https"
    entry_port      = 443
    target_protocol = "http"
    target_port     = 8000
    
    certificate_name = digitalocean_certificate.cert.name
  }
  
  healthcheck {
    protocol = "http"
    port     = 8000
    path     = "/health"
  }
  
  droplet_ids = [digitalocean_droplet.api_server.id]
}
```

---

## 9. Development Environment ✅ 100%

### 9.1 Makefile

```makefile
# Makefile
.PHONY: help install dev test lint format clean docker-up docker-down migrate

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  dev         Run development server"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean cache files"
	@echo "  docker-up   Start Docker services"
	@echo "  docker-down Stop Docker services"
	@echo "  migrate     Run database migrations"

install:
	pip install -r requirements/dev.txt
	pre-commit install

dev:
	uvicorn src.interface.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=85

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(name)"

setup-dev:
	make install
	make docker-up
	sleep 10
	make migrate
	python scripts/setup_initial_data.py
```

### 9.2 Development Configuration

```python
# src/interface/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from interface.api.routes import transactions, auth, health
from interface.api.middleware.logging_middleware import LoggingMiddleware
from interface.api.middleware.rate_limit_middleware import RateLimitMiddleware

app = FastAPI(
    title="Área Médica API",
    description="Banking Transaction Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Routes
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(transactions.router)

@app.on_event("startup")
async def startup_event():
    # Initialize services, database connections, etc.
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup resources
    pass
```

---

## 10. CI/CD Pipeline ⏳ 0%

### 10.1 GitHub Actions CI

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_areamedica
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements/dev.txt') }}
        
    - name: Install dependencies
      run: |
        pip install -r requirements/dev.txt
        
    - name: Lint with Ruff
      run: ruff check src/ tests/
    
    - name: Format check with Ruff
      run: ruff format --check src/ tests/
      
    - name: Type check with mypy
      run: mypy src/
      
    - name: Run tests
      run: pytest tests/ --cov=src --cov-report=xml --cov-fail-under=85
      env:
        DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_areamedica
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run Bandit security check
      run: |
        pip install bandit
        bandit -r src/
```

### 10.2 GitHub Actions CD

```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ secrets.REGISTRY_URL }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
        
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker/Dockerfile
        push: true
        tags: |
          ${{ secrets.REGISTRY_URL }}/areamedica-api:latest
          ${{ secrets.REGISTRY_URL }}/areamedica-api:${{ github.sha }}
          
    - name: Deploy to DigitalOcean
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.DO_HOST }}
        username: ${{ secrets.DO_USERNAME }}
        key: ${{ secrets.DO_SSH_KEY }}
        script: |
          cd /opt/areamedica-api
          docker-compose pull
          docker-compose up -d
          docker system prune -f
```

---

## 11. Monitoring & Observability 🚧 30%

### 11.1 Prometheus Metrics

```python
# src/infrastructure/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Business metrics
TRANSACTION_COUNT = Counter(
    'transactions_total',
    'Total transactions processed',
    ['status', 'bank']
)

BANESCO_API_CALLS = Counter(
    'banesco_api_calls_total',
    'Total calls to Banesco API',
    ['status', 'operation']
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            method = scope["method"]
            path = scope["path"]
            
            start_time = time.time()
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    duration = time.time() - start_time
                    
                    REQUEST_COUNT.labels(
                        method=method, 
                        endpoint=path, 
                        status_code=status_code
                    ).inc()
                    
                    REQUEST_DURATION.labels(
                        method=method, 
                        endpoint=path
                    ).observe(duration)
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
```

### 11.2 Structured Logging

```python
# src/infrastructure/monitoring/logging.py
import structlog
import logging
import os

def configure_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=os.sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
```

### 11.3 Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "Área Médica API Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Transaction Status",
        "targets": [
          {
            "expr": "transactions_total",
            "legendFormat": "{{status}}"
          }
        ]
      },
      {
        "title": "Banesco API Status",
        "targets": [
          {
            "expr": "rate(banesco_api_calls_total[5m])",
            "legendFormat": "{{status}}"
          }
        ]
      }
    ]
  }
}
```

---

## 12. Code Quality & Standards ✅ 100%

### 12.1 Configuration Files

```toml
# pyproject.toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "areamedica-api"
version = "1.0.0"
description = "Banking Transaction Management System"
authors = [
    {name = "José Cabrera", email = "jose@niokistudio.com"}
]
requires-python = ">=3.11"

[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["S101"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"

[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--tb=short"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests"
]

[tool.coverage.run]
source = ["src"]
omit = [
    "tests/*",
    "*/migrations/*",
    "*/__init__.py"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]
```

### 12.2 Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

## 13. Security Requirements ⏳ 0%

### 13.1 Security Headers Middleware

```python
# src/interface/api/middleware/security_middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
```

### 13.2 Input Validation & Sanitization

```python
# src/application/validators/input_validator.py
import re
from typing import Optional
import bleach

class InputValidator:
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate Venezuelan phone number format."""
        pattern = r'^04\d{9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_national_id(national_id: str) -> bool:
        """Validate Venezuelan national ID format."""
        pattern = r'^[VE]\d{4,8}$'
        return bool(re.match(pattern, national_id.upper()))
    
    @staticmethod
    def validate_reference(reference: str) -> bool:
        """Validate Banesco reference format."""
        pattern = r'^\d{9}$'
        return bool(re.match(pattern, reference))
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 500) -> str:
        """Sanitize text input to prevent XSS."""
        if not text:
            return ""
        
        # Remove HTML tags and limit length
        cleaned = bleach.clean(text, strip=True)
        return cleaned[:max_length]
    
    @staticmethod
    def validate_transaction_id(transaction_id: str) -> bool:
        """Validate transaction ID format."""
        # Allow alphanumeric and common separators
        pattern = r'^[A-Za-z0-9\-_]{1,100}$'
        return bool(re.match(pattern, transaction_id))
```

---

## 14. Performance Requirements ⏳ 0%

### 14.1 Caching Strategy

```python
# src/infrastructure/cache/redis_cache.py
import redis.asyncio as redis
import json
from typing import Optional, Any
import os

class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            encoding="utf-8",
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 300
    ) -> bool:
        """Set value in cache with TTL."""
        try:
            serialized_value = json.dumps(value, default=str)
            return await self.redis_client.setex(key, ttl, serialized_value)
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return await self.redis_client.delete(key)
        except Exception:
            return False
    
    async def get_banesco_transaction_cache_key(self, transaction_id: str) -> str:
        """Generate cache key for Banesco transaction."""
        return f"banesco:transaction:{transaction_id}"
```

### 14.2 Database Connection Pooling

```python
# src/infrastructure/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool
import os

class DatabaseManager:
    def __init__(self):
        self.engine = create_async_engine(
            os.getenv("DATABASE_URL"),
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=os.getenv("SQL_ECHO", "false").lower() == "true"
        )
    
    async def get_session(self) -> AsyncSession:
        async with AsyncSession(self.engine, expire_on_commit=False) as session:
            yield session
    
    async def close(self):
        await self.engine.dispose()
```

---

## 15. Testing Strategy 🚧 20%

### 15.1 Test Structure

```python
# tests/unit/test_transaction_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from application.services.transaction_service import TransactionService
from domain.entities.transaction import Transaction

class TestTransactionService:
    @pytest.fixture
    def mock_transaction_repo(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_banesco_client(self):
        return AsyncMock()
    
    @pytest.fixture
    def transaction_service(self, mock_transaction_repo, mock_banesco_client):
        return TransactionService(
            transaction_repo=mock_transaction_repo,
            banesco_client=mock_banesco_client
        )
    
    @pytest.mark.asyncio
    async def test_create_transaction_new(self, transaction_service, mock_transaction_repo, mock_banesco_client):
        # Arrange
        transaction_id = "TEST123"
        mock_transaction_repo.get_by_transaction_id.return_value = None
        mock_banesco_client.get_transaction_status.return_value = {
            "status": "COMPLETED",
            "details": {"amount": 100.0}
        }
        
        # Act
        result = await transaction_service.create_transaction(
            transaction_id=transaction_id,
            customer_data={},
            reference="123456789",
            bank="BANESCO"
        )
        
        # Assert
        assert result.transaction_id == transaction_id
        mock_transaction_repo.save.assert_called_once()

# tests/integration/test_banesco_integration.py
import pytest
import httpx
from infrastructure.external.banesco_client import BanescoClient

class TestBanescoIntegration:
    @pytest.fixture
    def banesco_client(self):
        return BanescoClient(
            base_url="http://localhost:8080",  # Mock server
            api_key="test-key"
        )
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_success(self, banesco_client):
        # This test requires a mock Banesco server
        # Implementation depends on test environment setup
        pass

# tests/e2e/test_api_endpoints.py
import pytest
from httpx import AsyncClient
from interface.api.main import app

class TestAPIEndpoints:
    @pytest.mark.asyncio
    async def test_create_transaction_endpoint(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transactions",
                json={
                    "transaction_id": "TEST123",
                    "customer": {
                        "full_name": "John Doe",
                        "phone": "04161234567",
                        "national_id": "V12345678",
                        "concept": "Test payment"
                    },
                    "reference": "123456789",
                    "bank": "BANESCO"
                },
                headers={"Authorization": "Bearer test-token"}
            )
        
        assert response.status_code == 201
        assert response.json()["transaction_id"] == "TEST123"
```

### 15.2 Test Configuration

```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from infrastructure.database.models import Base

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create test database."""
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/test_areamedica",
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def db_session(test_db):
    """Create database session for tests."""
    async_session = sessionmaker(
        test_db, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
```

---

## 16. Environment Configuration ✅ 100%

### 16.1 Environment Variables

```bash
# .env.example

# Application
APP_NAME=areamedica-api
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/areamedica
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Banesco Integration
BANESCO_API_URL=https://api.banesco.com/v1
BANESCO_API_KEY=your-banesco-api-key
BANESCO_TIMEOUT=30
BANESCO_RATE_LIMIT=2

# Monitoring
PROMETHEUS_PORT=9090
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn

# CORS
ALLOWED_ORIGINS=https://your-frontend-domain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE
ALLOWED_HEADERS=*

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,jpg,png

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600
```

### 16.2 Configuration Management

```python
# src/infrastructure/config/settings.py
from pydantic import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Application
    app_name: str = "areamedica-api"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 30
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300
    
    # Authentication
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Banesco
    banesco_api_url: str
    banesco_api_key: str
    banesco_timeout: int = 30
    banesco_rate_limit: int = 2
    
    # Monitoring
    log_level: str = "INFO"
    sentry_dsn: Optional[str] = None
    
    # CORS
    allowed_origins: List[str] = ["*"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

## 17. Additional Considerations ⏳ 0%

### 17.1 Missing Aspects for Consideration

Based on the analysis of the PRD and sequence diagram, here are additional aspects that should be considered for the ERD:

1. **Audit Trail Enhancement**
   - Complete audit logging for all user actions
   - Immutable audit logs with digital signatures
   - Compliance with financial regulations

2. **Data Backup and Recovery**
   - Automated database backups
   - Point-in-time recovery procedures
   - Disaster recovery planning

3. **API Versioning Strategy**
   - Clear API versioning scheme
   - Backward compatibility maintenance
   - Deprecation policies

4. **WebSocket Support (Future)**
   - Real-time transaction status updates
   - Live notifications for status changes

5. **Batch Processing**
   - Bulk transaction import/export
   - Scheduled reconciliation jobs
   - Report generation

6. **Multi-language Support**
   - i18n framework implementation
   - Translation management
   - Locale-specific formatting

7. **Advanced Security Features**
   - API key management for external integrations
   - Request signing and verification
   - Advanced threat detection

8. **Performance Optimization**
   - Database query optimization
   - Response compression
   - CDN integration for static assets

### 17.2 Implementation Priority

**Phase 1 (MVP - October 2025)**
- Core transaction management
- Basic authentication
- Banesco integration
- Basic monitoring

**Phase 2 (Post-MVP)**
- Advanced reporting
- Enhanced security features
- Performance optimizations
- WebSocket support

**Phase 3 (Future)**
- Multi-bank support
- Advanced analytics
- Mobile API enhancements
- Third-party integrations

### 17.3 Risk Mitigation Strategies

1. **Technical Risks**
   - Implement comprehensive testing (85% coverage requirement)
   - Use feature flags for risky deployments
   - Maintain staging environment identical to production

2. **Integration Risks**
   - Mock Banesco API for development/testing
   - Circuit breaker pattern for external API calls
   - Graceful degradation when external services fail

3. **Security Risks**
   - Regular security audits
   - Dependency vulnerability scanning
   - Penetration testing

4. **Performance Risks**
   - Load testing before production
   - Database performance monitoring
   - Auto-scaling configuration

---

## 📝 Next Steps (Priority Order)

### 🎯 Phase 1: Core Foundation (Current Focus)
- [ ] **Database Models** - Create SQLAlchemy models for all tables
  - Users, Permissions, UserPermissions
  - Transactions, TransactionEvents
  - RateLimits
- [ ] **Database Migrations** - Initial Alembic migration
- [ ] **API Endpoints** - Health checks (DONE ✅)
- [ ] **Basic Tests** - Health endpoint tests (DONE ✅)

### 🎯 Phase 2: Authentication (Next)
- [ ] JWT authentication service
- [ ] Login/Register endpoints
- [ ] Authentication middleware
- [ ] Permission-based authorization
- [ ] User management endpoints

### 🎯 Phase 3: Core Business Logic
- [ ] Transaction DTOs and validation
- [ ] Transaction repository implementation
- [ ] Transaction service layer
- [ ] Transaction CRUD endpoints
- [ ] Transaction listing with filters

### 🎯 Phase 4: Banesco Integration
- [ ] Banesco client implementation
- [ ] Rate limiting service
- [ ] Transaction status sync logic
- [ ] Error handling and retries
- [ ] Integration tests

### 🎯 Phase 5: Advanced Features
- [ ] Monitoring and metrics integration
- [ ] CI/CD pipeline setup
- [ ] Security enhancements
- [ ] Performance optimization
- [ ] Comprehensive test coverage (85%+)

---

This ERD provides a comprehensive foundation for developing the Área Médica backend API with all the specified requirements and additional considerations for a robust, production-ready system.