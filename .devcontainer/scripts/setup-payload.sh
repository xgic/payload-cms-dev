#!/usr/bin/env bash
set -euo pipefail

# Thin orchestration wrapper for the pexpect-based Payload CMS automation.
# Most logic (including idempotency) now lives in create-payload-automated.py.

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

log_info "setup" "Starting Payload CMS project automation..."

CONFIG_FILE=".devcontainer/create-payload-config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  log_warn "setup" "create-payload-config.json not found — using defaults"
else
  log_info "setup" "Using configuration from $CONFIG_FILE"
  log_debug "setup" "Config file resolved to: $CONFIG_FILE"
fi

python3 .devcontainer/scripts/create-payload-automated.py --config "$CONFIG_FILE"

log_success "setup" "Payload CMS automation completed."
