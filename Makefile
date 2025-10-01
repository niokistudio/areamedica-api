.PHONY: help install dev test lint format clean docker-up docker-down migrate setup-dev

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
	@echo "  setup-dev   Setup development environment"

install:
	pip install -r requirements/dev.txt
	pre-commit install

dev:
	uvicorn src.interface.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term-missing

lint:
	ruff check src/ tests/
	black --check src/ tests/
	mypy src/

format:
	ruff --fix src/ tests/
	black src/ tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf dist/ build/ *.egg-info/

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

migrate:
	alembic upgrade head

migrate-create:
	@if [ -z "$(name)" ]; then echo "Usage: make migrate-create name=migration_name"; exit 1; fi
	alembic revision --autogenerate -m "$(name)"

migrate-downgrade:
	alembic downgrade -1

setup-dev:
	@echo "Setting up development environment..."
	cp .env.example .env
	make install
	@echo "Please edit .env file with your configuration"
	@echo "Then run: make docker-up && make migrate"

db-reset:
	docker-compose down -v
	docker-compose up -d db redis
	sleep 5
	make migrate

# Production commands
build:
	docker build -f docker/Dockerfile -t areamedica-api .

run-prod:
	gunicorn src.interface.api.main:app -w 4 -k uvicorn.workers.UvicornWorker