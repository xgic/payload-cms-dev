#!/bin/bash
set -e

# This script runs on the host during initializeCommand (and via `make init-env`).
# It generates a secure .env file **only if one does not already exist**.
#
# This makes the script idempotent: repeated devcontainer rebuilds,
# `docker compose up`, or manual invocations will not rotate secrets
# and invalidate existing database data.
#
# To explicitly rotate credentials, use:
#   make env-regenerate
#   make reset-project --rotate-credentials   (or the Python script directly)

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

ENV_FILE=".devcontainer/.env"

# Idempotency guard: do not overwrite an existing .env file.
# On normal devcontainer startup/rebuilds we stay completely silent when nothing needs to be done.
if [ -f "$ENV_FILE" ]; then
    exit 0
fi

log_info "init-env" "Generating secure environment configuration..."

# PostgreSQL (non-interactive via env vars with sensible defaults)
PG_USER=${PG_USER:-payload}
PG_PASSWORD=${PG_PASSWORD:-$(openssl rand -hex 16)}

# Payload CMS
PAYLOAD_SECRET=${PAYLOAD_SECRET:-$(openssl rand -hex 32)}

# Read database name and user from create-payload-config.json when available (preferred)
CONFIG_FILE=".devcontainer/create-payload-config.json"
if [ -f "$CONFIG_FILE" ] && command -v jq >/dev/null 2>&1; then
    CONFIG_DB_NAME=$(jq -r '.dbName // empty' "$CONFIG_FILE" 2>/dev/null || true)
    CONFIG_DB_USER=$(jq -r '.dbUser // empty' "$CONFIG_FILE" 2>/dev/null || true)

    if [ -n "$CONFIG_DB_NAME" ]; then
        DB_NAME="$CONFIG_DB_NAME"
    else
        DB_NAME="payload_db"
    fi

    if [ -n "$CONFIG_DB_USER" ]; then
        PG_USER="$CONFIG_DB_USER"
    fi
else
    DB_NAME="payload_db"
fi

cat > "$ENV_FILE" << EOF
POSTGRES_USER=${PG_USER}
POSTGRES_PASSWORD=${PG_PASSWORD}
POSTGRES_DB=${DB_NAME}
PAYLOAD_SECRET=${PAYLOAD_SECRET}
DATABASE_URI=postgres://${PG_USER}:${PG_PASSWORD}@postgres:5432/${DB_NAME}
EOF

log_success "init-env" "Generated secure .env at $(pwd)/$ENV_FILE (POSTGRES_DB=${DB_NAME})"
log_info "init-env" "Payload project creation will occur inside the container (via postStartCommand / setup-payload.sh)."
