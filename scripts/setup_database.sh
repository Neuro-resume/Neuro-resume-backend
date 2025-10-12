#!/bin/bash
# Script to setup PostgreSQL database for Neuro Resume Backend

set -e

echo "🔧 Setting up PostgreSQL database for Neuro Resume Backend..."

# Database configuration
DB_NAME="neuro_resume"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Check if PostgreSQL is running
if ! sudo systemctl is-active --quiet postgresql; then
    echo "⚠️  PostgreSQL is not running. Starting..."
    sudo systemctl start postgresql
fi

# Create database if it doesn't exist
echo "📦 Creating database '$DB_NAME'..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"

echo "✅ Database '$DB_NAME' is ready!"

# Display connection info
echo ""
echo "📋 Database connection info:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""
echo "🔗 Connection string:"
echo "  postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo "✅ Database setup complete!"
