#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Determine the absolute path of the script directory and the project root
SCRIPT_DIR="$(python -c "import os, sys; print(os.path.abspath(os.path.dirname('$0')))")"
ROOT_DIR="$(python -c "import os, sys; print(os.path.abspath(os.path.join('$SCRIPT_DIR', '..')))")"

# Check if correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: ./scripts/run_test.sh <project_name> <app_name>"
    exit 1
fi

PROJECT_NAME=$1
APP_NAME=$2

# Specify the settings module for testing
export DJANGO_SETTINGS_MODULE=$PROJECT_NAME.test_settings

# Load environment variables from scripts/.test_env
echo "Loading environment variables from scripts/.test_env..."
if [ -f "$SCRIPT_DIR/.test_env" ]; then
    set -o allexport
    source "$SCRIPT_DIR/.test_env"
    set +o allexport
else
    echo "Error: Environment file '$SCRIPT_DIR/.test_env' not found."
    exit 1
fi

# Ensure TEST_DB_NAME is set
export TEST_DB_NAME=${TEST_DB_NAME:-ingest_db_test}

# Start Docker Compose services for db and redis
echo "Starting Docker Compose services (db and redis)..."
docker compose -f "$ROOT_DIR/docker-compose.yml" up -d db redis

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is up."

# Drop and recreate the test database to ensure a fresh state
echo "Resetting test database '$TEST_DB_NAME'..."
bash "$SCRIPT_DIR/database_setup.sh" reset "$TEST_DB_NAME"

# Run migrations on the test database
echo "Running migrations on test database..."
python "$ROOT_DIR/manage.py" migrate --settings="$DJANGO_SETTINGS_MODULE"

# Run tests with --keepdb to prevent Django from trying to drop the test database
echo "Running tests..."
python -m pytest --cov="$APP_NAME" --cov-report=term-missing "$ROOT_DIR"


# Bring down Docker Compose after tests
echo "Stopping Docker Compose..."
docker compose -f "$ROOT_DIR/docker-compose.yml" down

echo "Tests completed successfully."
