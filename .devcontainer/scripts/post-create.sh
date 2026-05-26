#!/bin/bash
#
# DEPRECATED / LEGACY COMPATIBILITY SHIM
# --------------------------------------
# This script is kept for backward compatibility with older Makefile targets
# and any external automation that still calls "post-create.sh".
#
# Payload project creation logic now lives in:
#   - .devcontainer/scripts/setup-payload.sh
#
# Note: The previous pexpect-based automation has been removed.
# See setup-payload.sh for current approach and limitations.
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
    log_warn "post-create" "setup-payload.sh not found — falling back to basic creation attempt"
    PROJECT_NAME=$(python3 .devcontainer/scripts/get-payload-project-name.py 2>/dev/null || echo "my-payload-cms")
    pnpx create-payload-app@latest "$PROJECT_NAME" -t website --use-pnpm --yes || true
fi

echo ""
log_info "post-create" "Consider using 'make post-create' or the new setup-payload.sh directly."