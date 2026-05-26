# Makefile for XGIC/payload-cms-dev-containers
# Highly optimized Payload CMS development environment using VS Code Dev
# Containers + Docker Compose. Adheres to XGIC project standards: clean
# architecture, self-documenting targets, industry best practices for DX,
# and strict Conventional Commits for all future changes.
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
POST_CREATE_SCRIPT ?= .devcontainer/scripts/setup-payload.sh
WORKSPACE_DIR      ?= /workspace

# Generated Payload project folder name (from config or fallback)
PAYLOAD_PROJECT_NAME ?= $(shell python3 .devcontainer/scripts/get-payload-project-name.py)

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

.PHONY: help up down build rebuild clean reset reset-project logs ps \
	shell prune env refresh-env \
	project-delete env-regenerate postgres-reset reset-db \
	init-env post-create lint-shell \
	validate validate-python test test-cov test-verbose exec python \
	test-in-container exec-shell \
	reset-project-py devcontainer-tests

# Guard: prevent destructive commands when running inside the Dev Container
define CONTAINER_GUARD
	@if [ -n "$$REMOTE_CONTAINERS" ] || [ -n "$$CODESPACES" ]; then \
		echo "❌ This command must be run from the host, not inside the" \
		     "Dev Container."; \
		exit 1; \
	fi
endef

help: ## Display this help message
	@echo "=== XGIC Payload CMS Dev Container Makefile ==="
	@echo "Usage: make <target>"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start all services in detached mode
	$(CONTAINER_GUARD)
	$(DOCKER_COMPOSE) up -d

down: ## Stop and remove containers (volumes and .env preserved)
	$(CONTAINER_GUARD)
	$(DOCKER_COMPOSE) down

build: ## Build or rebuild all services (no cache)
	$(CONTAINER_GUARD)
	$(DOCKER_COMPOSE) build --no-cache

# Full Dev Container lifecycle simulation (ideal for testing automation).
rebuild: clean init-env build up post-create ## Full lifecycle (clean + rebuild + post-create)

clean: ## ⚠️ DANGER: Full environment nuke (removes volumes + .env + generated project). Use `make reset-project` for the safer targeted reset.
	$(CONTAINER_GUARD)
	@echo "⚠️  WARNING: This will permanently delete:"
	@echo "   • All Docker volumes (including Payload CMS data)"
	@echo "   • Orphaned resources"
	@echo "   • The dynamically generated .devcontainer/.env file"
	@echo ""
	@read -p "Type 'yes' to continue (anything else cancels): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		$(DOCKER_COMPOSE) down -v --remove-orphans; \
		rm -f $(ENV_FILE); \
		echo "✅ Environment fully cleaned (including .devcontainer/.env)."; \
	else \
		echo "❌ Operation cancelled by user."; \
	fi

reset: clean ## Alias for clean (DANGER: full environment nuke)

# --- Atomic reset steps (still available individually) -----------------------
# Note: For normal development use `make reset-project` (stable credentials).
# env-regenerate is mainly useful for explicit credential rotation or testing.

project-delete: ## Delete only the generated Payload project folder
	@echo "Removing generated project folder ($(PAYLOAD_PROJECT_NAME))..."
	@rm -rf $(PAYLOAD_PROJECT_NAME)

env-regenerate: ## Regenerate .devcontainer/.env with fresh random credentials (explicit rotation)
	@echo "Regenerating fresh database credentials (.env)..."
	@rm -f $(ENV_FILE)
	@python3 .devcontainer/scripts/regenerate-env.py 2>/dev/null || \
		bash $(INIT_ENV_SCRIPT) 2>/dev/null || \
		echo "⚠️  Could not regenerate credentials."

postgres-reset reset-db: ## Reset only the Postgres service + data volume (fresh DB). DB name is taken from create-payload-config.json.
	@echo "Stopping and removing postgres service (with volumes)..."
	@$(DOCKER_COMPOSE) rm -f -s -v postgres 2>/dev/null || true
	@echo "Removing postgres volume..."
	@docker volume rm $(POSTGRES_VOLUME) 2>/dev/null || true
	@echo "Recreating postgres service..."
	@$(DOCKER_COMPOSE) up -d postgres || { \
		echo "❌ Failed to start postgres after reset."; \
		exit 1; \
	}
	@echo "Ensuring application database exists (from create-payload-config.json)..."
	@DB_NAME=$$(jq -r '.dbName // "payload_db"' .devcontainer/create-payload-config.json 2>/dev/null || echo "payload_db"); \
	DB_USER=$$(jq -r '.dbUser // "payload"' .devcontainer/create-payload-config.json 2>/dev/null || echo "payload"); \
	$(DOCKER_COMPOSE) exec -T postgres \
		psql -U "$$DB_USER" -d postgres -c "CREATE DATABASE $$DB_NAME OWNER $$DB_USER;" \
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
# Explicit rotation is still possible with the Python script's --rotate-credentials
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
# Note: No CONTAINER_GUARD is applied here. This target is intentionally
# allowed to run from inside the dev container (the Python script has good
# context detection and gives appropriate next-step advice either way).
reset-project: ## Fast targeted reset (project folder + Postgres volume). Safe to run inside or outside the container. Credentials are stable by default.
	@python3 .devcontainer/scripts/reset-project.py --compact $(if $(YES),--yes,)

reset-project-py: ## Direct / low-level alias for the Python reset script (useful for --dry-run, --rotate-credentials, etc.)
	@python3 .devcontainer/scripts/reset-project.py $(if $(YES),--yes,)

init-env: ## Run host-side init-env.sh
	@if [ -f $(INIT_ENV_SCRIPT) ]; then \
		echo "🚀 Running init-env.sh on host..."; \
		bash $(INIT_ENV_SCRIPT); \
	else \
		echo "⚠️  init-env.sh not found – skipping."; \
	fi

# Run the Payload project creation automation (uses setup-payload.sh)
post-create: ## Run Payload automation inside container
	@echo "🚀 Running Payload automation (workspace: $(WORKSPACE_DIR))..."
	$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c \
		"set -a; . '$(WORKSPACE_DIR)/$(ENV_FILE)' 2>/dev/null || true; set +a; \
		 cd '$(WORKSPACE_DIR)' && bash '$(WORKSPACE_DIR)/$(POST_CREATE_SCRIPT)'"

logs: ## Follow logs for all services
	$(DOCKER_COMPOSE) logs -f

ps: ## List running containers
	$(DOCKER_COMPOSE) ps

shell: ## Open interactive shell in the primary Payload CMS service
	$(CONTAINER_GUARD)
	@echo "Opening shell in workspace directory ($(WORKSPACE_DIR)) as node user..."
	@$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c \
		"cd '$(WORKSPACE_DIR)' 2>/dev/null || true && exec sh"

prune: ## Prune unused Docker objects system-wide (use with caution)
	docker system prune -f --volumes

env: ## Show current environment file status
	@echo "ENV_FILE = $(ENV_FILE)"
	@ls -la $(ENV_FILE) 2>/dev/null || echo "No .env file found."

refresh-env: ## Output the shell command to load the current .env (use: eval $(make refresh-env))
	@echo 'set -a; . $(ENV_FILE); set +a'

lint-shell: ## Run shellcheck on all shell scripts
	@command -v shellcheck > /dev/null 2>&1 || { \
		echo "❌ shellcheck not found. Install:"; \
		echo "   'apt install shellcheck' or 'brew install shellcheck'."; \
		exit 1; \
	}
	@echo "Running shellcheck..."
	shellcheck .devcontainer/scripts/*.sh
	@echo "✅ Shellcheck passed."

validate-python: ## Check Python syntax of scripts in .devcontainer/scripts (if any)
	@echo "Validating Python files in .devcontainer/scripts..."
	@find .devcontainer/scripts -name "*.py" -exec python3 -m py_compile {} + 2>/dev/null || true
	@echo "✅ Python validation passed (or no .py files present)."

# =============================================================================
# Container Execution Helpers (for working with Grok / AI agents)
# =============================================================================

# Run an arbitrary command inside the running dev container as the node user
exec: ## Run command in container (make exec CMD="...")
	@$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c "$(CMD)"

# Convenience target to run Python (from the venv) inside the container
python: ## Run Python in container venv (make python CMD="...")
	@$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c "python3 $(CMD)"

# Run pytest inside the container (uses the venv's pytest)
test-in-container: ## Run pytest inside the Dev Container
	@$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c \
		"python3 -m pytest $(ARGS)"

devcontainer-tests: ## Run the devcontainer environment validation tests (.devcontainer/scripts/devcontainer-tests.sh)
	@if [ -n "$$REMOTE_CONTAINERS" ] || [ -n "$$CODESPACES" ]; then \
		echo "▶ Running devcontainer tests inside container..."; \
		bash .devcontainer/scripts/devcontainer-tests.sh; \
	else \
		echo "▶ Running devcontainer tests inside container via docker compose exec..."; \
		$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) bash .devcontainer/scripts/devcontainer-tests.sh; \
	fi

# Open an interactive shell (already exists as 'shell', kept for clarity)
exec-shell: shell ## Alias for 'shell' (interactive shell inside container)

# =============================================================================
# Testing (requires pytest + pytest-cov + pytest-mock)
# These targets prefer the Dev Container's venv when available.
# =============================================================================

PYTEST := $(shell command -v pytest 2>/dev/null || echo python3 -m pytest)

test: ## Run unit tests
	$(PYTEST)

test-cov: ## Run tests with coverage (HTML in htmlcov/)
	$(PYTEST) --cov=.devcontainer/scripts \
		--cov-report=term-missing --cov-report=html

test-verbose: ## Run tests with maximum verbosity
	$(PYTEST) -vv

coverage: test-cov ## Alias for test-cov
	@echo "Coverage report generated in htmlcov/"

# Run all practical host-side validation (lint + tests).
validate: validate-python lint-shell test ## Run validation (lint+tests)
	@echo "✅ All host-side validation passed."
