#!/bin/bash
set -e

# Source shared logging (with graceful fallback if the lib is missing, e.g. after a hard clean)
LOGGING_LIB="$(dirname "$0")/lib/logging.sh"
if [ -f "$LOGGING_LIB" ]; then
  # shellcheck source=lib/logging.sh
  source "$LOGGING_LIB"
else
  # Minimal fallback so scripts still work
  log_info()  { echo "[$1] $2"; }
  log_success() { echo "[$1] $2"; }
  log_warn()  { echo "[$1] $2" >&2; }
  log_error() { echo "[$1] $2" >&2; }
  log_debug() { :; }
fi

# Note: Tests are intended to be runnable at different points in the devcontainer
# lifecycle. Some checks may be expected to fail until the full setup (including
# Payload project creation) has completed.

log_info "tests" "Starting devcontainer-tests.sh script..."
printf '\n%s\n' "$(date)"

echo "Check Node.js version."
node --version

echo "Check pnpm version."
pnpm --version

echo "Check PostgreSQL Client version."
psql --version

echo "Check PostgreSQL database access."

CONFIG_FILE=".devcontainer/create-payload-config.json"
DB_NAME="payload_db"
DB_USER="${POSTGRES_USER:-payload}"

if [ -f "$CONFIG_FILE" ] && command -v jq >/dev/null 2>&1; then
    CONFIG_DB_NAME=$(jq -r '.dbName // empty' "$CONFIG_FILE" 2>/dev/null || true)
    CONFIG_DB_USER=$(jq -r '.dbUser // empty' "$CONFIG_FILE" 2>/dev/null || true)

    [ -n "$CONFIG_DB_NAME" ] && DB_NAME="$CONFIG_DB_NAME"
    [ -n "$CONFIG_DB_USER" ] && DB_USER="$CONFIG_DB_USER"
fi

PGHOST=${PGHOST:-postgres} \
PGPASSWORD=${POSTGRES_PASSWORD} psql -U "${DB_USER}" \
  -d "$DB_NAME" -c "\l" --no-password -h "${PGHOST}"

echo "Check Docker CLI (best practice test)."
docker --version
docker info --format "Docker Engine: {{.ServerVersion}}"

echo ""
log_info "tests" "Ending devcontainer-tests.sh script..."
printf '\n%s\n' "$(date)"