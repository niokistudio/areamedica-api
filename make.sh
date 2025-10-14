#!/bin/bash
# Alternative to Makefile for Windows users

case "$1" in
  help)
    echo "Available commands:"
    echo "  ./make.sh install     Install dependencies"
    echo "  ./make.sh dev         Run development server"
    echo "  ./make.sh test        Run tests"
    echo "  ./make.sh test-cov    Run tests with coverage"
    echo "  ./make.sh lint        Run linting"
    echo "  ./make.sh format      Format code"
    echo "  ./make.sh clean       Clean cache files"
    echo "  ./make.sh docker-up   Start Docker services"
    echo "  ./make.sh docker-down Stop Docker services"
    echo "  ./make.sh docker-logs View Docker logs"
    echo "  ./make.sh migrate     Run database migrations"
    echo "  ./make.sh setup-dev   Setup development environment"
    echo "  ./make.sh db-reset    Reset database"
    echo "  ./make.sh build       Build production image"
    ;;

  install)
    pip install -r requirements/dev.txt
    pre-commit install
    ;;

  dev)
    uvicorn src.interface.api.main:app --reload --host 0.0.0.0 --port 8000
    ;;

  test)
    pytest
    ;;

  test-cov)
    pytest --cov=src --cov-report=html --cov-report=term-missing
    ;;

  lint)
    ruff check src/ tests/
    ruff format --check src/ tests/
    mypy src/
    ;;

  format)
    ruff check --fix src/ tests/
    ruff format src/ tests/
    ;;

  clean)
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
    rm -rf dist/ build/ *.egg-info/
    ;;

  docker-up)
    docker-compose up -d
    echo "Waiting for database to be ready..."
    sleep 5
    alembic upgrade head
    ;;

  docker-down)
    docker-compose down
    ;;

  docker-logs)
    docker-compose logs -f
    ;;

  migrate)
    alembic upgrade head
    ;;

  migrate-create)
    if [ -z "$2" ]; then 
      echo "Usage: ./make.sh migrate-create <migration_name>"
      exit 1
    fi
    alembic revision --autogenerate -m "$2"
    ;;

  migrate-downgrade)
    alembic downgrade -1
    ;;

  setup-dev)
    echo "Setting up development environment..."
    cp .env.example .env
    ./make.sh install
    echo "Please edit .env file with your configuration"
    echo "Then run: ./make.sh docker-up"
    ;;

  db-reset)
    docker-compose down -v
    docker-compose up -d db redis
    sleep 5
    ./make.sh migrate
    ;;

  build)
    docker build -f docker/Dockerfile -t areamedica-api .
    ;;

  run-prod)
    gunicorn src.interface.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
    ;;

  *)
    echo "Unknown command: $1"
    echo "Run './make.sh help' for available commands"
    exit 1
    ;;
esac
