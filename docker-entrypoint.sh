#!/bin/sh

# Wait for postgres to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z ${DB_HOST} ${DB_PORT}; do
  sleep 0.1
done
echo "PostgreSQL is ready!"

# Run migrations
echo "Running database migrations..."
poetry run alembic upgrade head

# Start the application
echo "Starting the application..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
