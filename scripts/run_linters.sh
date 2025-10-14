#!/bin/bash

# Wrapper script to execute static analysis tools

set -euo pipefail

cd "$(dirname "$0")/.."

printf '🔍 Running black --check...\n'
black --check .

printf '🐍 Running mypy...\n'
mypy .

printf '🪶 Running flake8...\n'
flake8 .

printf '✅ Linters passed successfully!\n'
