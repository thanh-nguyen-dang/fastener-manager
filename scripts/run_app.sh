#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Determine the absolute path of the script directory and the project root
SCRIPT_DIR="$(python -c "import os, sys; print(os.path.abspath(os.path.dirname('$0')))")"
ROOT_DIR="$(python -c "import os, sys; print(os.path.abspath(os.path.join('$SCRIPT_DIR', '..')))")"

# Check if correct number of arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./scripts/run_app.sh <project_name>"
    exit 1
fi

PROJECT_NAME=$1

# Specify the settings module for the application
export DJANGO_SETTINGS_MODULE=$PROJECT_NAME.settings

# Function to load .env file
load_env_file() {
    ENV_FILE_PATH=$1
    if [ -f "$ENV_FILE_PATH" ]; then
        echo "Loading environment variables from $ENV_FILE_PATH..."
        set -o allexport
        source "$ENV_FILE_PATH"
        set +o allexport
    else
        echo "Error: Environment file '$ENV_FILE_PATH' not found."
        return 1
    fi
}

# Try to load the .env file from SCRIPT_DIR first
if ! load_env_file "$SCRIPT_DIR/.env"; then
    # If not found, try to load from ROOT_DIR
    if ! load_env_file "$ROOT_DIR/.env"; then
        echo "Error: No .env file found in either '$SCRIPT_DIR' or '$ROOT_DIR'."
        exit 1
    fi
fi

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

# Create the main database if it doesn't exist
echo "Ensuring main database '$DB_NAME' exists..."
bash "$SCRIPT_DIR/database_setup.sh" create "$DB_NAME"

# Run migrations on the main database
echo "Running migrations on main database..."
python "$ROOT_DIR/manage.py" migrate --settings="$DJANGO_SETTINGS_MODULE"

# Start the Django development server
echo "Starting Django development server..."
python "$ROOT_DIR/manage.py" runserver 0.0.0.0:8000 --settings="$DJANGO_SETTINGS_MODULE"
