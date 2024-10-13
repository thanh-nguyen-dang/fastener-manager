#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Ensure required environment variables are set
: "${DB_USER:?Need to set DB_USER}"
: "${DB_PASSWORD:?Need to set DB_PASSWORD}"
: "${DB_HOST:?Need to set DB_HOST}"
: "${DB_PORT:?Need to set DB_PORT}"
: "${DB_SCHEMA:?Need to set DB_SCHEMA}"

# Function to create a database if it doesn't exist
create_database() {
    local db_name=$1
    echo "Checking if database '$db_name' exists..."
    DB_EXISTS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -tAc "SELECT 1 FROM pg_database WHERE datname='$db_name'")
    if [ "$DB_EXISTS" = "1" ]; then
        echo "Database '$db_name' already exists."
    else
        echo "Creating database '$db_name'..."
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -c "CREATE DATABASE \"$db_name\" OWNER \"$DB_USER\";"
    fi
}

# Function to drop a database if it exists
drop_database() {
    local db_name=$1
    echo "Dropping database '$db_name' if it exists..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -c "DROP DATABASE IF EXISTS \"$db_name\";"
}

# Function to create schema and grant permissions
setup_schema() {
    local db_name=$1
    echo "Creating schema '$DB_SCHEMA' in database '$db_name' if it doesn't exist..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$db_name" -c "CREATE SCHEMA IF NOT EXISTS \"$DB_SCHEMA\" AUTHORIZATION \"$DB_USER\";"
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$db_name" -c "SET SEARCH_PATH=$DB_SCHEMA,public;"

    echo "Granting USAGE and CREATE privileges on schema '$DB_SCHEMA' to user '$DB_USER' in database '$db_name'..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$db_name" -c "GRANT USAGE, CREATE ON SCHEMA \"$DB_SCHEMA\" TO \"$DB_USER\";"

    echo "Granting all privileges on all tables, sequences, and functions in schema '$DB_SCHEMA' to user '$DB_USER' in database '$db_name'..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$db_name" -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA \"$DB_SCHEMA\" TO \"$DB_USER\";"
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$db_name" -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA \"$DB_SCHEMA\" TO \"$DB_USER\";"
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$db_name" -c "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA \"$DB_SCHEMA\" TO \"$DB_USER\";"
}

# Function to display usage information
usage() {
    echo "Usage: $0 {create|drop|reset} <database_name>"
    echo "  create <database_name>  - Create the specified database and set up schema."
    echo "  drop <database_name>    - Drop the specified database."
    echo "  reset <database_name>   - Drop and recreate the specified database, then set up schema."
    exit 1
}

# Check if at least two arguments are provided
if [ $# -lt 2 ]; then
    usage
fi

# Parse command-line arguments
action="$1"
db_name="$2"

case "$action" in
    create)
        create_database "$db_name"
        setup_schema "$db_name"
        ;;
    drop)
        drop_database "$db_name"
        ;;
    reset)
        drop_database "$db_name"
        create_database "$db_name"
        setup_schema "$db_name"
        ;;
    *)
        echo "Unknown action: $action"
        usage
        ;;
esac

echo "Action '$action' completed successfully for database '$db_name'."
