#!/bin/bash
#
# DEPRECATED / LEGACY COMPATIBILITY SHIM
# --------------------------------------
# This script is kept for backward compatibility with older Makefile targets
# and any external automation that still calls "post-create.sh".
#
# The authoritative Payload creation automation now lives in:
#   - .devcontainer/scripts/setup-payload.sh  (thin wrapper)
#   - .devcontainer/scripts/create-payload-automated.py  (pexpect-based CLI)
#
# The old direct creation logic and inline validation have been removed.
# See the new Python script for configuration via create-payload-config.json.
#
# TODO (future): Move the SQLTools credential patching logic into a dedicated step.
#

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

log_warn "post-create" "This legacy script is deprecated."
log_warn "post-create" "Delegating to the current automation flow..."

# Delegate to the current thin wrapper (best effort compatibility)
if [ -x ".devcontainer/scripts/setup-payload.sh" ]; then
    exec bash .devcontainer/scripts/setup-payload.sh
else
    log_warn "post-create" "setup-payload.sh not found — falling back to direct Python call"
    python3 .devcontainer/scripts/create-payload-automated.py --config .devcontainer/create-payload-config.json || true
fi

echo ""
log_info "post-create" "Consider using 'make post-create' or the new setup-payload.sh directly."