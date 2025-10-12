# Área Médica API

Banking Transaction Management System with Banesco integration.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Make (optional but recommended)

### Development Setup

1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd areamedica-api
   make setup-dev
   ```

2. **Configure environment:**
   ```bash
   # Edit .env file with your configuration
   cp .env.example .env
   # Update DATABASE_URL, BANESCO_API_KEY, SECRET_KEY, etc.
   ```

3. **Start services:**
   ```bash
   make docker-up
   make migrate
   ```

4. **Run the application:**
   ```bash
   make dev
   ```

The API will be available at: http://localhost:8000

## 📖 Documentation

### API Documentation
- **Complete API Docs**: [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md) - Guía completa con ejemplos de endpoints, errores estandarizados, autenticación JWT, y datos de prueba
- **CSV Reference**: [`api_requests_responses.csv`](./api_requests_responses.csv) - Referencia rápida de requests/responses
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Additional Docs
- **Development Summary**: [`DEVELOPMENT_SUMMARY.md`](./DEVELOPMENT_SUMMARY.md)
- **ERD Documentation**: [`ERD-Backend-API.md`](./ERD-Backend-API.md)
- **Terraform Deployment**: [`terraform/README.md`](./terraform/README.md)

## 🛠️ Development Commands

```bash
# Setup development environment
make setup-dev

# Install dependencies
make install

# Run development server
make dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Lint code
make lint

# Format code
make format

# Clean cache files
make clean

# Docker commands
make docker-up      # Start all services
make docker-down    # Stop all services
make docker-logs    # View logs

# Database migrations
make migrate                    # Run migrations
make migrate-create name="..."  # Create new migration
make migrate-downgrade         # Downgrade last migration

# Reset database (WARNING: destroys all data)
make db-reset
```

## 🏗️ Project Structure

```
areamedica-api/
├── src/                    # Source code
│   ├── domain/            # Core business logic
│   ├── application/       # Use cases and services
│   ├── infrastructure/    # External dependencies
│   └── interface/         # Controllers and routes
├── tests/                 # Test files
├── migrations/            # Database migrations
├── docker/               # Docker configurations
├── monitoring/           # Prometheus & Grafana configs
├── scripts/              # Utility scripts
└── requirements/         # Python dependencies
```

## 🐳 Docker Services

- **API**: FastAPI application (port 8000)
- **Database**: PostgreSQL 15 (port 5432)
- **Cache**: Redis 7 (port 6379)
- **Monitoring**: Prometheus (port 9090)
- **Dashboards**: Grafana (port 3000)

## 🔧 Configuration

All configuration is done through environment variables. See `.env.example` for available options.

Key configurations:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string  
- `BANESCO_API_KEY`: Banesco API authentication key
- `SECRET_KEY`: JWT token signing key

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test types
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/e2e/           # End-to-end tests only
```

Target coverage: **85%** for `src/` directory.

## 📊 Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## 🚀 Deployment

### Option 1: Koyeb (Recommended for Testing/MVP)

Koyeb deployment using Infrastructure as Code with `koyeb.yaml`:

```bash
# 1. Connect your repository to Koyeb
# 2. Select "Docker" deployment
# 3. Koyeb will auto-detect koyeb.yaml
# 4. Configure environment variables
# 5. Deploy!
```

**Features**:
- ✅ 100% Free tier (no credit card required)
- ✅ Auto-deploy from `main` branch
- ✅ Automatic migrations via start script
- ✅ Health checks on `/health`
- ✅ PostgreSQL via Neon integration
- ✅ SSL certificates automatic
- ✅ Always active (no sleep)

**Cost**: **FREE** (512 MB RAM, 2 GB storage)

### Option 2: DigitalOcean (IaC with Terraform)

Infrastructure as Code deployment using Terraform:

```bash
cd terraform/

# Initialize Terraform
terraform init

# Review changes
terraform plan

# Deploy infrastructure
terraform apply

# See outputs
terraform output
```

📖 **Terraform Guide**: See [`terraform/README.md`](./terraform/README.md)

**Features**:
- ✅ Complete infrastructure as code
- ✅ VPC network isolation
- ✅ Managed PostgreSQL cluster
- ✅ Redis cache
- ✅ Droplet with Docker
- ✅ Monitoring with Prometheus/Grafana

### Option 3: Docker Compose (Development/Testing)

```bash
# Build and start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

### Option 4: Manual Production Build

```bash
# Build production image
make build

# Run production server
make run-prod
```

### Environment Variables for Production

**Critical variables to configure**:
```bash
SECRET_KEY=your_production_secret_key_here  # Generate with: openssl rand -hex 32
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0
BANESCO_API_KEY=your_banesco_api_key
ENVIRONMENT=production
DEBUG=false
```

See `.env.production.example` for complete list.

### Deployment Checklist

Before deploying to production:

- [ ] Set `SECRET_KEY` to a strong random value
- [ ] Configure Banesco API credentials
- [ ] Set `DEBUG=false`
- [ ] Configure `CORS_ORIGINS` with your frontend domains
- [ ] Run migrations: `alembic upgrade head`
- [ ] Verify health check: `curl https://your-domain.com/health`
- [ ] Configure SSL certificates
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy for database

## 📋 API Endpoints

### Health Checks
- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check

### Transactions (Coming Soon)
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions/{id}` - Get transaction
- `GET /api/v1/transactions/{id}/status` - Get status with Banesco sync
- `GET /api/v1/transactions` - List transactions

### Authentication (Coming Soon)
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token

## 🔒 Security

- JWT-based authentication
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy
- Rate limiting for Banesco API calls
- CORS configuration
- Security headers middleware

## 📝 Code Quality

This project enforces high code quality standards:

- **Linting & Formatting**: Ruff (replaces both Flake8 and Black)
- **Type checking**: MyPy
- **Testing**: pytest with 85% coverage requirement
- **Pre-commit hooks**: Automated quality checks

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests: `make test`
4. Run linting: `make lint`  
5. Format code: `make format`
6. Commit with descriptive message
7. Create pull request

## 📄 License

[MIT License](LICENSE)

## 📞 Support

For issues and questions, please create an issue in the repository.