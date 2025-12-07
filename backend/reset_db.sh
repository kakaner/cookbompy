#!/bin/bash

# Database reset script for CookBomPy
# This script deletes the database and reinitializes it with fresh migrations
# Can be run from project root or backend directory

set -e  # Exit on error

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"  # Change to backend directory

echo "⚠️  WARNING: This will delete all data in the database!"
read -p "Are you sure you want to reset the database? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Database reset cancelled."
    exit 0
fi

# Get the database file path from the environment or use default
if [ -f .env ]; then
    # Try to extract DATABASE_URL from .env
    DB_URL=$(grep "^DATABASE_URL=" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'")
else
    DB_URL="sqlite:///./cookbompy.db"
fi

# Check if using SQLite
if [[ "$DB_URL" == sqlite* ]]; then
    # Extract the database file path
    DB_FILE=$(echo "$DB_URL" | sed 's|sqlite:///\./||' | sed 's|sqlite://||')
    
    if [ -f "$DB_FILE" ]; then
        echo "Deleting database file: $DB_FILE"
        rm "$DB_FILE"
        echo "✓ Database file deleted"
    else
        echo "Database file not found: $DB_FILE (may not exist yet)"
    fi
else
    echo "⚠️  Warning: Non-SQLite database detected: $DB_URL"
    echo "This script only handles SQLite databases."
    echo "For PostgreSQL, you'll need to manually drop and recreate the database."
    read -p "Continue anyway? (yes/no): " continue_anyway
    if [ "$continue_anyway" != "yes" ]; then
        exit 0
    fi
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run migrations to recreate the database
echo ""
echo "Running migrations to recreate database..."
alembic upgrade head

echo ""
echo "✓ Database reset complete!"
echo "The database has been deleted and reinitialized with fresh schema."

