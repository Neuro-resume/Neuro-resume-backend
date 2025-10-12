#!/bin/bash
# Migration management script for Alembic

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Using .env.example as template."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_info "Created .env file from .env.example"
    else
        print_error ".env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Main script logic
case "$1" in
    "upgrade")
        print_info "Running migrations (upgrade to head)..."
        alembic upgrade head
        print_info "Migrations completed successfully!"
        ;;
    "downgrade")
        if [ -z "$2" ]; then
            print_error "Please specify revision to downgrade to (e.g., -1 for previous revision)"
            exit 1
        fi
        print_info "Downgrading database to revision: $2"
        alembic downgrade "$2"
        print_info "Downgrade completed successfully!"
        ;;
    "revision")
        if [ -z "$2" ]; then
            print_error "Please provide migration message (e.g., './scripts/migrate.sh revision \"create users table\"')"
            exit 1
        fi
        print_info "Creating new migration: $2"
        alembic revision --autogenerate -m "$2"
        print_info "Migration file created successfully!"
        ;;
    "current")
        print_info "Current database revision:"
        alembic current
        ;;
    "history")
        print_info "Migration history:"
        alembic history --verbose
        ;;
    "heads")
        print_info "Current head revisions:"
        alembic heads
        ;;
    *)
        echo "Usage: $0 {upgrade|downgrade|revision|current|history|heads}"
        echo ""
        echo "Commands:"
        echo "  upgrade              - Apply all pending migrations"
        echo "  downgrade <revision> - Downgrade to specific revision (e.g., -1 for previous)"
        echo "  revision <message>   - Create new migration with autogenerate"
        echo "  current              - Show current database revision"
        echo "  history              - Show migration history"
        echo "  heads                - Show current head revisions"
        echo ""
        echo "Examples:"
        echo "  $0 upgrade"
        echo "  $0 downgrade -1"
        echo "  $0 revision \"create users table\""
        exit 1
        ;;
esac
