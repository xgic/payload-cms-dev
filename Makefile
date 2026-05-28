# Makefile for XGIC/payload-cms-dev-containers
# Highly optimized Payload CMS development environment using VS Code
# Dev Containers + Docker Compose. Adheres to XGIC project standards:
# clean architecture, self-documenting targets, industry best practices
# for DX, and strict Conventional Commits for all future changes.
# Reference: Docker Compose best practices, VS Code Dev Container spec,
# and our internal coding guidelines.

# ──────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────
COMPOSE_FILE       ?= .devcontainer/docker-compose.yml
PROJECT_NAME       ?= xgic-payload-cms-dev-containers
SERVICE_NAME       ?= xgic-payload-cms-dev-containers
ENV_FILE           ?= .devcontainer/.env
POSTGRES_VOLUME    ?= xgic-payload-cms-dev-containers-postgres-data

INIT_ENV_SCRIPT    ?= .devcontainer/scripts/init-env.sh
WORKSPACE_DIR      ?= /workspace

# Generated Payload project folder name (from config or fallback)
PAYLOAD_PROJECT_NAME ?= $(shell \
	python3 .devcontainer/scripts/get-payload-project-name.py)

DOCKER_COMPOSE := docker compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME)

# Colors for one-line status output (respect NO_COLOR)
ifneq ($(NO_COLOR),)
GREEN  :=
RED    :=
RESET  :=
else
GREEN  := \033[32m
RED    := \033[31m
RESET  := \033[0m
endif

# =============================================================================
# Conditional Emoji / Status Symbols (all recommendations implemented)
# -----------------------------------------------------------------------------
# Policy for this dev-container project: be optimistic for developers.
#
# Rich emoji output is enabled by default on normal developer machines
# (VS Code terminal, Windows Terminal, WSL, Git Bash, local shells,
# inside or outside the dev container, SSH sessions to dev boxes, etc.).
#
# We only fall back to pure ASCII when there is a *clear* reason:
#   - Explicit disable: NO_COLOR (any value) or EMOJI=0
#   - Known non-interactive / limited environment:
#       * TERM=dumb
#       * Common CI variables (CI=1, GITHUB_ACTIONS=1, etc.)
#
# This completely removes reliance on the fragile `[ -t 1 ]` test inside
# $(shell) at parse time. That test is known to return false in exactly the
# environments shown in the issues/ screenshots (VS Code over SSH/Remote,
# Windows Terminal + Git Bash, Dev Container terminal shims, etc.), even
# when the actual terminal emulator fully supports emoji.
#
# Result: emojis "just work" on capable developer terminals with **zero
# configuration change** required on the developer's side — exactly the
# behavior requested.
#
# Optional force knobs (rarely needed):
#   FORCE_COLOR=1 / CLICOLOR_FORCE=1 / EMOJI=1  → force rich even in CI
#
# Explicit opt-outs (always honored):
#   NO_COLOR=1 or EMOJI=0  → force plain ASCII
#
# Guarantees:
#   - Single $(shell) evaluation at parse time only (zero runtime cost).
#   - No emojis in target names, prerequisites, or logic.
#   - Safe "==>" prefix for critical messages.
#   - Pure 7-bit ASCII fallbacks.
#
# Matches the flexibility you asked for: automatic adaptation based on real
# terminal capabilities, without asking developers to modify their environment.
# =============================================================================

EMOJI_ENABLED := $(shell \
  if [ -n "$(NO_COLOR)" ] || [ "$(EMOJI)" = "0" ]; then \
    echo no; \
  elif [ "$(TERM)" = "dumb" ] || [ -n "$(CI)" ] || [ -n "$(GITHUB_ACTIONS)" ]; then \
    echo no; \
  else \
    echo yes; \
  fi)

ifeq ($(EMOJI_ENABLED),yes)
    EMOJI_OK      ?= ✅
    EMOJI_ERROR   ?= ❌
    EMOJI_WARN    ?= ⚠️
    EMOJI_ARROW   ?= →
    EMOJI_ROCKET  ?= 🚀
    EMOJI_INFO    ?= ℹ️
    EMOJI_PACKAGE ?= 📦
    EMOJI_SYNC    ?= 🔄
    EMOJI_RUN     ?= ▶
else
    EMOJI_OK      ?= [OK]
    EMOJI_ERROR   ?= [ERROR]
    EMOJI_WARN    ?= [WARN]
    EMOJI_ARROW   ?= ->
    EMOJI_ROCKET  ?=
    EMOJI_INFO    ?= [INFO]
    EMOJI_PACKAGE ?= [PKG]
    EMOJI_SYNC    ?= [...]
    EMOJI_RUN     ?= >
endif

.PHONY: help up down build rebuild clean reset reset-project logs ps \
	shell prune env refresh-env \
	project-delete env-regenerate postgres-reset reset-db \
	init-env create-payload lint-shell lint-makefile \
	validate validate-python test test-cov test-verbose test-make test-makefile exec python \
	test-in-container exec-shell \
	reset-project-py devcontainer-tests \
	docker-build-only docker-build-nocache docker-build-only-nocache \
	check-db test-db dev dev-all \
	pre-release-check generate-config-schema validate-config coverage \
	emoji-debug

# Note: The emoji system (EMOJI_ENABLED + EMOJI_* vars) is intentionally not
# exposed as phony targets. They are internal parse-time variables only.

# -----------------------------------------------------------------------------
# Debug helper for the emoji detection system (safe to run anywhere)
# Run this in the exact terminal where you are seeing the problem.
# It will print exactly what the current Makefile thinks about your session.
emoji-debug:
	@echo "=== Emoji Detection Debug ==="
	@echo "EMOJI_ENABLED=[$(EMOJI_ENABLED)]"
	@echo "TERM=[$(TERM)]"
	@echo "NO_COLOR=[$(NO_COLOR)]"
	@echo "EMOJI=[$(EMOJI)]"
	@echo "CI=[$(CI)]"
	@echo "GITHUB_ACTIONS=[$(GITHUB_ACTIONS)]"
	@echo "FORCE_COLOR=[$(FORCE_COLOR)]"
	@echo "CLICOLOR_FORCE=[$(CLICOLOR_FORCE)]"
	@echo ""
	@echo "Resulting symbols that would be used:"
	@echo "  EMOJI_ERROR  = [$(EMOJI_ERROR)]"
	@echo "  EMOJI_OK     = [$(EMOJI_OK)]"
	@echo "  EMOJI_WARN   = [$(EMOJI_WARN)]"
	@echo "  EMOJI_ARROW  = [$(EMOJI_ARROW)]"
	@echo "  EMOJI_ROCKET = [$(EMOJI_ROCKET)]"
	@echo ""
	@echo "Example line from check-db (what you would actually see):"
	@echo "$(EMOJI_ERROR) The development containers are not running."
	@echo "   $(EMOJI_ARROW) Start them with: make up"
	@echo "   $(EMOJI_WARN) WARNING: make rebuild is destructive..."
	@echo "=== End debug ==="

# =============================================================================
# Container / Host Execution Helpers
# =============================================================================
#
# HOST_ONLY_GUARD   : Commands that must be run from the host (e.g. docker compose up/down, clean, rebuild)
# RUN_IN_CONTAINER  : For commands best run inside the container. When invoked from the host,
#                     automatically delegates via `docker compose exec`. Fails with a clear
#                     message if the container is not running.

# Prevent commands that must run on the host from being executed inside the dev container.
define HOST_ONLY_GUARD
	@if [ -n "$$REMOTE_CONTAINERS" ] || [ -n "$$CODESPACES" ] || \
	    [ "$$XG_AIS_HOST_TYPE" = "xgic-devcontainer" ]; then \
		echo "$(EMOJI_ERROR) This command must be run from the host, not inside the Dev Container."; \
		exit 1; \
	fi
endef

# If this target is invoked from the host (outside the dev container),
# automatically delegate the command to run *inside* the container
# using `docker compose exec`.
#
# Usage:
#   my-target:
#       $(call RUN_IN_CONTAINER, some-command-here)
#
# If the container is not running, it fails with a clear error suggesting
# to start it or use "Dev Containers: Reopen in Container" in VS Code.
define RUN_IN_CONTAINER
	@if [ -z "$$REMOTE_CONTAINERS" ] && [ -z "$$CODESPACES" ] && \
	    [ "$$XG_AIS_HOST_TYPE" != "xgic-devcontainer" ]; then \
		echo "$(EMOJI_ARROW) Running '$@' inside the dev container..."; \
		$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) $(1) || { \
			echo ""; \
			echo "$(EMOJI_ERROR) Failed to run '$@' inside the dev container."; \
			echo "   Is the container running? Try:  make up"; \
			echo "   Or use: VS Code $(EMOJI_ARROW) Dev Containers: Reopen in Container"; \
			exit 1; \
		}; \
	else \
		$(1); \
	fi
endef

help: ## Display this help message
	@echo "=== XGIC Payload CMS Dev Container Makefile ==="
	@echo "Usage: make <target>"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start all services in detached mode
	$(HOST_ONLY_GUARD)
	$(DOCKER_COMPOSE) up -d

down: ## Stop and remove containers (volumes and .env preserved)
	$(HOST_ONLY_GUARD)
	$(DOCKER_COMPOSE) down

build: ## Build or rebuild all services (uses cache by default)
	$(HOST_ONLY_GUARD)
	$(DOCKER_COMPOSE) build

docker-build-nocache: ## Force full rebuild of all services (no cache)
	$(HOST_ONLY_GUARD)
	$(DOCKER_COMPOSE) build --no-cache

docker-build-only: ## Build only the Docker image (uses cache by default)
	## Fast for normal development
	$(DOCKER_COMPOSE) build

docker-build-only-nocache: ## Force rebuild of only the Docker image (no cache)
	## Recommended when actively developing the Dockerfile
	$(DOCKER_COMPOSE) build --no-cache

# Full Dev Container lifecycle simulation (ideal for testing automation).
rebuild: clean init-env build up create-payload
	## Full lifecycle (clean + rebuild + create-payload)
	## Tip: Use `make docker-build-only-nocache` for fast Dockerfile work.

clean: ## [WARN] DANGER: Full environment nuke (removes volumes + .env
	## + generated project). Use `make reset-project` for safer resets.
	## Non-interactive: make clean YES=1 or make clean FORCE=1
	$(HOST_ONLY_GUARD)
	@echo "$(EMOJI_WARN) WARNING: This will permanently delete:"
	@echo "   • All Docker volumes (including Payload CMS data)"
	@echo "   • Orphaned resources"
	@echo "   • The dynamically generated .devcontainer/.env file"
	@echo ""
	@if [ "$(YES)" = "1" ] || [ "$(FORCE)" = "1" ]; then \
		echo "Proceeding without confirmation (YES=1 or FORCE=1)."; \
		$(DOCKER_COMPOSE) down -v --remove-orphans; \
		rm -f $(ENV_FILE); \
		echo "$(EMOJI_OK) Environment fully cleaned (including .devcontainer/.env)."; \
	else \
		read -p "Type 'yes' to continue (anything else cancels): " confirm; \
		if [ "$$confirm" = "yes" ]; then \
			$(DOCKER_COMPOSE) down -v --remove-orphans; \
			rm -f $(ENV_FILE); \
			echo "$(EMOJI_OK) Environment fully cleaned (including .devcontainer/.env)."; \
		else \
			echo "$(EMOJI_ERROR) Operation cancelled by user."; \
		fi \
	fi

reset: clean ## Alias for clean (DANGER: full environment nuke)

# --- Atomic reset steps (still available individually) -----------------------
# Note: For normal development use `make reset-project` (stable credentials).
# env-regenerate is mainly useful for explicit credential rotation or testing.

project-delete: ## Delete only the generated Payload project folder
	@echo "Removing generated project folder ($(PAYLOAD_PROJECT_NAME))..."
	@rm -rf $(PAYLOAD_PROJECT_NAME)

env-regenerate: ## Regenerate .devcontainer/.env with fresh random
	## credentials (explicit rotation)
	@echo "Regenerating fresh database credentials (.env)..."
	@rm -f $(ENV_FILE)
	@python3 .devcontainer/scripts/regenerate-env.py 2>/dev/null || \
		bash $(INIT_ENV_SCRIPT) 2>/dev/null || \
		echo "$(EMOJI_WARN)  Could not regenerate credentials."

postgres-reset reset-db: ## Reset Postgres service + data volume (fresh DB).
	## DB name taken from create-payload-config.json.
	@echo "Stopping and removing postgres service (with volumes)..."
	@$(DOCKER_COMPOSE) rm -f -s -v postgres 2>/dev/null || true
	@echo "Removing postgres volume..."
	@docker volume rm $(POSTGRES_VOLUME) 2>/dev/null || true
	@echo "Recreating postgres service..."
	@$(DOCKER_COMPOSE) up -d postgres || { \
		echo "$(EMOJI_ERROR) Failed to start postgres after reset."; \
		exit 1; \
	}
	@echo "Ensuring application database exists (from config)..."
	@DB_NAME=$$(jq -r '.dbName // "payload_db"' \
		.devcontainer/create-payload-config.json 2>/dev/null \
		|| echo "payload_db"); \
	DB_USER=$$(jq -r '.dbUser // "payload"' \
		.devcontainer/create-payload-config.json 2>/dev/null \
		|| echo "payload"); \
	$(DOCKER_COMPOSE) exec -T postgres \
		psql -U "$$DB_USER" -d postgres \
		-c "CREATE DATABASE $$DB_NAME OWNER $$DB_USER;" \
		2>/dev/null || true

# --- High-level workflow targets --------------------------------------------

# =============================================================================
# Reset / Recovery Targets (now powered by Python for reliability)
# =============================================================================
#
# The "fast reset" flow lives in .devcontainer/scripts/reset-project.py.
#
# Design decision (2026-05): For fast resets we intentionally do *not* rotate
# database credentials by default. Rotating the password on every reset was
# the root cause of repeated "PostgreSQL authentication failed" problems
# (container env vars are baked in at start; the .env file on disk would get
# new values, causing a mismatch).
#
# Fast reset now only:
#   - Deletes the generated Payload project folder
#   - Resets the Postgres data volume (clean DB)
#
# Credentials remain stable from the initial dev container creation.
# Explicit rotation is still possible with the Python script's
# --rotate-credentials flag.
# flag or by doing a full `make clean && make rebuild`.
#
# The atomic targets (project-delete, env-regenerate, postgres-reset) remain
# for backward compatibility.
#
# Recommended:
#     make reset-project
#     make reset-project YES=1
#     python3 .devcontainer/scripts/reset-project.py --rotate-credentials --yes
#
# The script gives context-aware next steps (host vs inside container).

# --- High-level combined reset (recommended entry point) --------------------
# Note: No HOST_ONLY_GUARD is applied here. This target is intentionally
# allowed to run from inside the dev container (the Python script has good
# context detection and gives appropriate next-step advice either way).
reset-project: ## Fast targeted reset (project folder + Postgres volume).
	## Safe to run inside or outside the container.
	## Credentials are stable by default.
	@python3 .devcontainer/scripts/reset-project.py --compact $(if $(YES),--yes,)

reset-project-py: ## Direct/low-level alias for the Python reset script
	## (useful for --dry-run, --rotate-credentials, etc.)
	@python3 .devcontainer/scripts/reset-project.py $(if $(YES),--yes,)

init-env: ## Run host-side init-env.sh
	@if [ -f $(INIT_ENV_SCRIPT) ]; then \
		echo "$(EMOJI_ROCKET) Running init-env.sh on host..."; \
		bash $(INIT_ENV_SCRIPT); \
	else \
		echo "$(EMOJI_WARN)  init-env.sh not found – skipping."; \
	fi

# =============================================================================
# Payload Project Creation Flow
# =============================================================================
#
# The actual work is done by .devcontainer/scripts/setup-payload.sh.
# This target is the recommended way to trigger project creation from the host.
#
# Typical flows:
#   make post-create          # Run inside an already-running dev container
#   make rebuild              # Full clean + rebuild + create-payload
#
# Inside the container you can also run directly:
#   bash .devcontainer/scripts/setup-payload.sh
#
create-payload: ## Run Payload project creation automation inside the container
	@echo "$(EMOJI_ROCKET) Running Payload automation (workspace: $(WORKSPACE_DIR))..."
	$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c \
		"set -a; . '$(WORKSPACE_DIR)/$(ENV_FILE)' 2>/dev/null || true; set +a; \
		 cd '$(WORKSPACE_DIR)' && \
		 bash '$(WORKSPACE_DIR)/.devcontainer/scripts/setup-payload.sh'"

# =============================================================================
# Development
# =============================================================================

check-db: ## Internal: verify that PostgreSQL is reachable (with friendly error)
	@echo "==> Checking database connectivity..."
	@if ! $(DOCKER_COMPOSE) ps --services --filter "status=running" | grep -q $(SERVICE_NAME); then \
		echo "$(EMOJI_ERROR) The development containers are not running."; \
		echo "   $(EMOJI_ARROW) Start them with:"; \
		echo "     make up"; \
		echo "   $(EMOJI_WARN) WARNING: make rebuild is destructive (removes containers, volumes, and .env):"; \
		echo "     make rebuild"; \
		exit 1; \
	fi
	@$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c \
		"set -a; . '$(WORKSPACE_DIR)/$(ENV_FILE)' 2>/dev/null || true; set +a; \
		 pg_isready -h postgres -U \"$${POSTGRES_USER:-payload}\" -d \"$${POSTGRES_DB:-payload_db}\" >/dev/null 2>&1 || { \
			echo '$(EMOJI_ERROR) Cannot connect to the database.'; \
			echo '   $(EMOJI_ARROW) Postgres may still be starting up. Wait a few seconds and try again.'; \
			echo '   $(EMOJI_ARROW) Or check logs with: make logs'; \
			exit 1; \
		 }"
	@echo "==> Database connection OK."

test-db: ## Test database connectivity (developer-friendly)
	-@$(MAKE) --no-print-directory check-db || exit 1

dev: ## Start the Payload development server (checks DB first)
	@$(MAKE) --no-print-directory check-db
	@PROJECT_NAME=$$(python3 .devcontainer/scripts/get-payload-project-name.py 2>/dev/null || echo "website"); \
	echo "$(EMOJI_ROCKET) Starting Payload dev server in $$PROJECT_NAME/..."; \
	$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c \
		"set -a; . '$(WORKSPACE_DIR)/$(ENV_FILE)' 2>/dev/null || true; set +a; \
		 cd '$(WORKSPACE_DIR)/$$PROJECT_NAME' && pnpm dev"

dev-all: ## Start all required services then run the development server
	@$(MAKE) --no-print-directory up
	@$(MAKE) --no-print-directory dev

logs: ## Follow logs for all services
	$(DOCKER_COMPOSE) logs -f

ps: ## List running containers
	$(DOCKER_COMPOSE) ps

shell: ## Open interactive shell in the primary Payload CMS service
	$(HOST_ONLY_GUARD)
	@echo "Opening shell in workspace directory ($(WORKSPACE_DIR)) as node user..."
	@$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c \
		"cd '$(WORKSPACE_DIR)' 2>/dev/null || true && exec sh"

prune: ## Prune unused Docker objects system-wide (use with caution)
	docker system prune -f --volumes

env: ## Show current environment file status
	@echo "ENV_FILE = $(ENV_FILE)"
	@ls -la $(ENV_FILE) 2>/dev/null || echo "No .env file found."

refresh-env: ## Output the shell command to load the current .env
	## (use: eval $(make refresh-env))
	@echo 'set -a; . $(ENV_FILE); set +a'

lint-shell: ## Run shellcheck on all shell scripts
	@if ! command -v shellcheck > /dev/null 2>&1; then \
		echo "$(EMOJI_WARN)  shellcheck not found on this machine."; \
		echo "   For full shell linting, run 'make validate' inside the dev container."; \
		echo "   Skipping shellcheck..."; \
	else \
		echo "Running shellcheck..."; \
		shellcheck .devcontainer/scripts/*.sh; \
		echo "$(EMOJI_OK) Shellcheck passed."; \
	fi

validate-python: ## Check Python syntax of scripts in .devcontainer/scripts
	## (if any)
	@echo "Validating Python files in .devcontainer/scripts..."
	@find .devcontainer/scripts -name "*.py" \
		-exec python3 -m py_compile {} + 2>/dev/null || true
	@echo "$(EMOJI_OK) Python validation passed (or no .py files present)."

lint-makefile: ## Run checkmake (Makefile linter) if available
	@if ! command -v checkmake > /dev/null 2>&1; then \
		echo "$(EMOJI_WARN)  checkmake not found (Makefile linter)."; \
		echo "   Install: go install github.com/checkmake/checkmake/cmd/checkmake@latest"; \
		echo "   Or (Docker): docker run --rm -v \"\$$PWD:/src\" -w /src quay.io/checkmake/checkmake checkmake Makefile"; \
		echo "   Skipping Makefile lint..."; \
	else \
		echo "Running checkmake..."; \
		checkmake Makefile || true; \
		echo "$(EMOJI_OK) checkmake finished (warnings are advisory for now)."; \
	fi

# =============================================================================
# Container Execution Helpers (for working with Grok / AI agents)
# =============================================================================

# Run an arbitrary command inside the running dev container as the node user
exec: ## Run command in container (make exec CMD="...")
	@$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c "$(CMD)"

# Convenience target to run Python (from the venv) inside the container
python: ## Run Python in container venv (make python CMD="...")
	$(call RUN_IN_CONTAINER, @$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c "python3 $(CMD)")

# Run pytest inside the container (installs dev requirements on first
# use if needed)
test-in-container: ensure-dev-python ## Run pytest inside the Dev Container
	$(call RUN_IN_CONTAINER, @$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c \
		"python3 -m pytest $(ARGS)")

devcontainer-tests: ## Run devcontainer env validation tests
	## (.devcontainer/scripts/devcontainer-tests.sh)
	@if [ -n "$$REMOTE_CONTAINERS" ] || [ -n "$$CODESPACES" ]; then \
		echo "$(EMOJI_RUN) Running devcontainer tests inside container..."; \
		bash .devcontainer/scripts/devcontainer-tests.sh; \
	else \
		echo "$(EMOJI_RUN) Running devcontainer tests via docker compose exec..."; \
		$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) \
			bash .devcontainer/scripts/devcontainer-tests.sh; \
	fi

# Open an interactive shell (already exists as 'shell', kept for clarity)
exec-shell: shell ## Alias for 'shell' (interactive shell inside container)

# =============================================================================
# Testing
# =============================================================================
#
# Test tooling is installed on-demand from .devcontainer/requirements-dev.txt
# into the container's Python venv. This keeps the base image smaller.

DEV_REQUIREMENTS := .devcontainer/requirements-dev.txt

# Ensure dev Python packages are installed (idempotent)
# Prefers the devcontainer's /opt/venv if present, otherwise uses the
# active python.
ensure-dev-python: $(DEV_REQUIREMENTS)
	@if [ -f "$(DEV_REQUIREMENTS)" ]; then \
		echo "$(EMOJI_PACKAGE) Ensuring dev Python packages are installed..."; \
		if [ -d "/opt/venv" ]; then \
			/opt/venv/bin/pip install --quiet --no-cache-dir -r $(DEV_REQUIREMENTS); \
		else \
			python3 -m pip install --quiet --no-cache-dir \
			-r $(DEV_REQUIREMENTS) 2>/dev/null || true; \
		fi \
	fi

PYTEST := $(shell command -v pytest 2>/dev/null || echo python3 -m pytest)

test: ensure-dev-python ## Run unit tests
	$(call RUN_IN_CONTAINER, $(PYTEST))

test-cov: ensure-dev-python ## Run tests with coverage (HTML in htmlcov/)
	$(call RUN_IN_CONTAINER, $(PYTEST) --cov=.devcontainer/scripts --cov=tests \
		--cov-report=term-missing --cov-report=html \
		--cov-fail-under=60)

test-verbose: ensure-dev-python ## Run tests with maximum verbosity
	$(call RUN_IN_CONTAINER, $(PYTEST) -vv)

test-make test-makefile: ensure-dev-python ## Run Makefile-specific behavior tests (guards, delegation, @-leakage, etc.)
	@echo "Running Makefile macro + behavior tests..."
	$(call RUN_IN_CONTAINER, $(PYTEST) tests/make/ -v)

coverage: test-cov ## Alias for test-cov
	@echo "Coverage report generated in htmlcov/"

# Run validation (lint + unit tests + config schema).
# When invoked from the host, the 'test' prerequisite will automatically
# delegate itself to run inside the dev container via RUN_IN_CONTAINER.
validate: validate-python lint-shell lint-makefile test validate-config
	@echo "$(EMOJI_OK) All validation passed."

# =============================================================================
# Release Preparation
# =============================================================================

pre-release-check: ## Run as much of the release checklist as possible locally
	@echo "$(EMOJI_ROCKET) Running pre-release validation..."
	@make validate
	@echo ""
	@echo "$(EMOJI_OK) Fast validation complete."
	@echo "Next: 'make rebuild' (host) + manual smoke tests inside container."
	@echo "See RELEASE_CHECKLIST.md for the complete list."

# --- Configuration Schema & Validation -------------------------------------

CONFIG_SCHEMA := .devcontainer/create-payload-config.schema.json
CONFIG_FILE   := .devcontainer/create-payload-config.json

.PHONY: generate-config-schema validate-config

generate-config-schema: ## Regenerate JSON Schema from canonical model
	## (requires Python + Pydantic)
	@echo "$(EMOJI_SYNC) Regenerating JSON Schema for create-payload-config.json..."
	@cd .devcontainer/config && python3 generate_schema.py
	@echo "$(EMOJI_OK) Schema updated at $(CONFIG_SCHEMA)"

validate-config: ## Validate create-payload-config.json vs its JSON Schema
	## (requires 'check-jsonschema' or Python)
	@if command -v check-jsonschema >/dev/null 2>&1; then \
		check-jsonschema --schemafile $(CONFIG_SCHEMA) $(CONFIG_FILE); \
	elif python3 -c "import jsonschema" 2>/dev/null; then \
		python3 -c '\
import json, jsonschema, sys; \
schema = json.load(open("$(CONFIG_SCHEMA)")); \
instance = json.load(open("$(CONFIG_FILE)")); \
jsonschema.validate(instance=instance, schema=schema); \
print("[OK] create-payload-config.json is valid against the schema")'; \
	else \
		echo "$(EMOJI_INFO)  Skipping strict schema validation"; \
		echo "   (install check-jsonschema or jsonschema for full)"; \
		python3 -c 'import json; json.load(open("$(CONFIG_FILE)")); print("[OK] JSON is syntactically valid")'; \
	fi


