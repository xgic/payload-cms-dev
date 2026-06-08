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

# Read rich configuration from the single source of truth.
# Non-secret values (template, adapter type, project name, etc.) come from the JSON.
# Secrets (passwords in connection strings, PAYLOAD_SECRET) are taken from the
# live environment when available (sourced by the Makefile post-create exec and
# init-env.sh). This prevents authentication issues between the running container and the generated `.env` file.
# seen in results.txt when the JSON contains a placeholder password.
CONFIG_FILE=".devcontainer/create-payload-config.json"

if [ -f "$CONFIG_FILE" ] && command -v jq >/dev/null 2>&1; then
    TEMPLATE=$(jq -r '.template // "website"' "$CONFIG_FILE" 2>/dev/null || echo "website")
    DB_ADAPTER=$(jq -r '.dbAdapter // "postgres"' "$CONFIG_FILE" 2>/dev/null || echo "postgres")
    JSON_DB_URI=$(jq -r '.dbUri // empty' "$CONFIG_FILE" 2>/dev/null || true)
    AGENT_FLAG=$(jq -r '.agent // "none"' "$CONFIG_FILE" 2>/dev/null || echo "none")
else
    TEMPLATE="website"
    DB_ADAPTER="postgres"
    JSON_DB_URI=""
    AGENT_FLAG="none"
fi

# Prefer live environment secrets (the ones the postgres container was actually started with)
# over anything in the static JSON. The post-create target does:
#   set -a; . '/workspace/.devcontainer/.env'; set +a
LIVE_DATABASE_URI="${DATABASE_URI:-}"
LIVE_PAYLOAD_SECRET="${PAYLOAD_SECRET:-}"

# Choose the connection string we will feed to create-payload-app
if [ -n "$LIVE_DATABASE_URI" ]; then
    DB_URI_FOR_CLI="$LIVE_DATABASE_URI"
elif [ -n "$JSON_DB_URI" ]; then
    DB_URI_FOR_CLI="$JSON_DB_URI"
else
    DB_URI_FOR_CLI=""
fi

# Normalize agent value into the actual CLI flag
if [ "$AGENT_FLAG" = "none" ] || [ -z "$AGENT_FLAG" ]; then
    AGENT_CLI_FLAG="--no-agent"
else
    AGENT_CLI_FLAG="--agent $AGENT_FLAG"
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

log_info "setup" "Starting Payload CMS project creation for '$PROJECT_NAME' (template: $TEMPLATE, db: $DB_ADAPTER)..."

# Fully non-interactive invocation using the real supported flags from
# create-payload-app (see packages/create-payload-app/src/lib/select-db.ts and select-agent.ts).
# This eliminates the "Select a database" and "Enter PostgreSQL connection string"
# prompts (and the coding agent prompt).
CREATE_CMD=(pnpx create-payload-app@latest "$PROJECT_NAME" -t "$TEMPLATE" --use-pnpm)

# Database (critical for Postgres + internal compose hostname)
if [ -n "$DB_URI_FOR_CLI" ]; then
    CREATE_CMD+=(--db "$DB_ADAPTER" --db-connection-string "$DB_URI_FOR_CLI")
else
    # Fallback: still declare the adapter (user will get a recommended string)
    CREATE_CMD+=(--db "$DB_ADAPTER" --db-accept-recommended)
fi

# Agent skill (usually none inside a disposable dev container)
if [ -n "$AGENT_CLI_FLAG" ]; then
    CREATE_CMD+=($AGENT_CLI_FLAG)
fi

# Suppress the pnpm "Ignored build scripts" warning for @swc/core (a
# dependency pulled in by next.js / Turbopack etc. during project creation).
# This is the root cause of the prominent warning box seen during
# `Dev Containers: Reopen in Container`.
# Running it here (before create-payload-app triggers the pnpm install)
# is safe, non-interactive, and idempotent.
corepack pnpm approve-builds @swc/core || true

log_debug "setup" "Invoking: ${CREATE_CMD[*]}"

if "${CREATE_CMD[@]}" 2>&1; then
  log_success "setup" "Payload project created successfully (non-interactively)."

  # Post-creation sync: ensure the generated project's .env has the exact live
  # credentials from the devcontainer environment. This is a defensive measure
  # because create-payload-app + manage-env-files may rewrite or normalize the
  # connection string and PAYLOAD_SECRET it receives.
  if [ -d "$PROJECT_NAME" ]; then
      GEN_ENV="$PROJECT_NAME/.env"
      if [ -f "$GEN_ENV" ]; then
          if [ -n "$LIVE_DATABASE_URI" ]; then
              # The website template uses DATABASE_URL
              sed -i "s|^DATABASE_URL=.*|DATABASE_URL=${LIVE_DATABASE_URI}|" "$GEN_ENV" || true
              log_debug "setup" "Synced DATABASE_URL in $GEN_ENV from live environment"
          fi
          if [ -n "$LIVE_PAYLOAD_SECRET" ]; then
              sed -i "s|^PAYLOAD_SECRET=.*|PAYLOAD_SECRET=${LIVE_PAYLOAD_SECRET}|" "$GEN_ENV" || true
              log_debug "setup" "Synced PAYLOAD_SECRET in $GEN_ENV from live environment"
          fi
      fi
  fi
else
  EXIT_CODE=$?
  log_warn "setup" "create-payload-app exited with status $EXIT_CODE."
  log_warn "setup" "This is often harmless (idempotency or minor warnings). Check the project directory."
  log_warn "setup" "If the project is incomplete, you can re-run manually inside the container:"
  log_warn "setup" "    bash .devcontainer/scripts/setup-payload.sh"
  # We intentionally do not hard-fail the devcontainer startup.
fi

# "finished" message intentionally omitted on the happy path for quieter devcontainer output.
# Specific success/warning messages above provide enough context when work is performed.
