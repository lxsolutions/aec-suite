





#!/bin/sh

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h db -p 5432; do
    echo "PostgreSQL not available, waiting..."
    sleep 1
done

echo "PostgreSQL is available"

# Apply database migrations if needed
if [ "$1" = 'uvicorn' ]; then
    echo "Applying database migrations..."
    alembic upgrade head
fi

exec "$@"


