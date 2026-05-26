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

# Note: The idempotency guard for Payload creation has been centralized in
# create-payload-automated.py. Tests can safely run regardless of project state.

log_info "tests" "Starting devcontainer-tests.sh script..."
printf '\n%s\n' "$(date)"

echo "Check Node.js version."
node --version

echo "Check pnpm version."
pnpm --version

echo "Check PostgreSQL Client version."
psql --version

echo "Check PostgreSQL database access."
PGPASSWORD=${POSTGRES_PASSWORD} psql -U "${POSTGRES_USER}" \
  -d payload_db -c "\l" --no-password

echo "Check Docker CLI (best practice test)."
docker --version
docker info --format "Docker Engine: {{.ServerVersion}}"

echo ""
log_info "tests" "Ending devcontainer-tests.sh script..."
printf '\n%s\n' "$(date)"