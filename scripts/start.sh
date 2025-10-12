#!/bin/bash
set -e

echo "==> Starting AreaMédica API..."

# Get port from environment or use default
PORT=${PORT:-8000}

echo "==> Port: $PORT"

# Run migrations if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "==> Running database migrations..."
    alembic upgrade head || echo "⚠️  Migration failed - will start anyway"
fi

echo "==> Starting uvicorn server..."

# Start the application
exec uvicorn src.interface.api.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers 1 \
    --log-level info
