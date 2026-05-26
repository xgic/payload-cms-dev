#!/usr/bin/env bash
set -euo pipefail

# Thin wrapper for Payload project creation during devcontainer setup.
#
# Uses a best-effort non-interactive invocation of create-payload-app.
# The creation is designed to be idempotent (see logic below).

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

# Determine project name from the canonical helper (respects create-payload-config.json)
PROJECT_NAME=$(python3 .devcontainer/scripts/get-payload-project-name.py 2>/dev/null || echo "my-payload-cms")

# Try to read template from config, with a safe default
CONFIG_FILE=".devcontainer/create-payload-config.json"
if [ -f "$CONFIG_FILE" ] && command -v jq >/dev/null 2>&1; then
    TEMPLATE=$(jq -r '.template // "website"' "$CONFIG_FILE" 2>/dev/null || echo "website")
else
    TEMPLATE="website"
fi

# Robust idempotency check:
# The Payload config lives in src/ in the standard template (src/payload.config.ts).
# We check both the root and src/ for flexibility.
if [ -d "$PROJECT_NAME" ] && {
      [ -f "$PROJECT_NAME/payload.config.ts" ] || [ -f "$PROJECT_NAME/payload.config.js" ] ||
      [ -f "$PROJECT_NAME/src/payload.config.ts" ] || [ -f "$PROJECT_NAME/src/payload.config.js" ];
   }; then
  # Project already exists — stay silent for a clean devcontainer startup experience.
  exit 0
fi

# If a directory exists but doesn't look like a completed Payload project, warn the user.
if [ -d "$PROJECT_NAME" ]; then
    log_warn "setup" "Directory '$PROJECT_NAME' exists but does not appear to be a complete Payload project."
    log_warn "setup" "The creation step may fail or produce unexpected results."
fi

log_info "setup" "Starting Payload CMS project creation for '$PROJECT_NAME' (template: $TEMPLATE)..."

# Try a best-effort non-interactive invocation.
# This may not work perfectly with all versions of create-payload-app.
if pnpx create-payload-app@latest "$PROJECT_NAME" \
    -t "$TEMPLATE" \
    --use-pnpm \
    --yes 2>&1; then
  log_success "setup" "Payload project created successfully."
else
  log_warn "setup" "Non-interactive creation did not complete cleanly."
  log_warn "setup" "You may need to run the Payload wizard manually inside the container:"
  log_warn "setup" "    pnpx create-payload-app@latest"
  log_error "setup" "Payload project creation step finished with warnings."
  # Do not fail hard — let the developer decide how to proceed
fi

# "finished" message intentionally omitted on the happy path for quieter devcontainer output.
# Specific success/warning messages above provide enough context when work is performed.
