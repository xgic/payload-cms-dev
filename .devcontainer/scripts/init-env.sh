#!/bin/bash
set -e

# Note: Idempotency for Payload project creation is now handled authoritatively
# inside .devcontainer/scripts/create-payload-automated.py (the pexpect automation).
# This script always runs on the host to (re)generate a secure .env if needed.

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

log_info "init-env" "Generating secure environment configuration..."

# PostgreSQL (non-interactive via env vars with sensible defaults)
PG_USER=${PG_USER:-payload}
PG_PASSWORD=${PG_PASSWORD:-$(openssl rand -hex 16)}

# Payload CMS
PAYLOAD_SECRET=${PAYLOAD_SECRET:-$(openssl rand -hex 32)}

cat > .devcontainer/.env << EOF
POSTGRES_USER=${PG_USER}
POSTGRES_PASSWORD=${PG_PASSWORD}
PAYLOAD_SECRET=${PAYLOAD_SECRET}
DATABASE_URI=postgres://${PG_USER}:${PG_PASSWORD}@postgres:5432/payload_db
EOF

log_success "init-env" "Generated secure .env at $(pwd)/.devcontainer/.env"
log_info "init-env" "Payload project creation will occur inside the container via postCreateCommand."
