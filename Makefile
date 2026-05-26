# Makefile for XGIC/payload-cms-dev-containers
# Highly optimized Payload CMS development environment using VS Code Dev
# Containers + Docker Compose. Adheres to XGIC project standards: clean
# architecture, self-documenting targets, industry best practices for DX,
# and strict Conventional Commits for all future changes.
# Reference: Docker Compose best practices, VS Code Dev Container spec,
# and our internal coding guidelines.

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
COMPOSE_FILE       ?= .devcontainer/docker-compose.yml
PROJECT_NAME       ?= xgic-payload-cms-dev-containers
SERVICE_NAME       ?= xgic-payload-cms-dev-containers
ENV_FILE           ?= .devcontainer/.env

INIT_ENV_SCRIPT    ?= .devcontainer/scripts/init-env.sh
POST_CREATE_SCRIPT ?= .devcontainer/scripts/setup-payload.sh
WORKSPACE_DIR      ?= /workspace

DOCKER_COMPOSE := docker compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME)

.PHONY: help up down build rebuild clean reset logs ps shell prune env init-env post-create lint-shell validate validate-python test test-cov test-verbose exec python test-in-container exec-shell

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

rebuild: clean init-env build up post-create ## ⚡ Full Dev Container lifecycle simulation (ideal for testing)

clean: ## ⚠️ DANGER: Completely reset environment (removes volumes + .env)
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

reset: clean ## Alias for clean

init-env: ## Run host-side init-env.sh
	@if [ -f $(INIT_ENV_SCRIPT) ]; then \
		echo "🚀 Running init-env.sh on host..."; \
		bash $(INIT_ENV_SCRIPT); \
	else \
		echo "⚠️  init-env.sh not found – skipping."; \
	fi

post-create: ## Run the Payload automation inside the container (uses setup-payload.sh + Python pexpect automation)
	@echo "🚀 Running Payload creation automation inside container (workspace: $(WORKSPACE_DIR))..."
	$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c \
		"cd '$(WORKSPACE_DIR)' && bash '$(WORKSPACE_DIR)/$(POST_CREATE_SCRIPT)'"

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

lint-shell: ## Run shellcheck on all shell scripts (requires shellcheck to be installed)
	@command -v shellcheck > /dev/null 2>&1 || { \
		echo "❌ shellcheck is not installed. Please install it (e.g. 'apt install shellcheck' or 'brew install shellcheck')."; \
		exit 1; \
	}
	@echo "Running shellcheck..."
	shellcheck .devcontainer/scripts/*.sh
	@echo "✅ Shellcheck passed."

validate-python: ## Check Python syntax and basic structure of automation scripts
	@echo "Validating Python automation script..."
	@python3 -m py_compile .devcontainer/scripts/create-payload-automated.py
	@python3 -c "import ast; ast.parse(open('.devcontainer/scripts/create-payload-automated.py').read()); print('  - AST parse: OK')"
	@echo "✅ Python validation passed."

# =============================================================================
# Container Execution Helpers (for working with Grok / AI agents)
# =============================================================================

# Run an arbitrary command inside the running dev container as the node user
exec: ## Run a command inside the container (usage: make exec CMD="your command here")
	@$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c "$(CMD)"

# Convenience target to run Python (from the venv) inside the container
python: ## Run Python inside the container's venv (usage: make python CMD="script.py --arg")
	@$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c "python3 $(CMD)"

# Run pytest inside the container (uses the venv's pytest)
test-in-container: ## Run pytest inside the Dev Container
	@$(DOCKER_COMPOSE) exec --user node $(SERVICE_NAME) sh -c "python3 -m pytest $(ARGS)"

# Open an interactive shell (already exists as 'shell', kept for clarity)
exec-shell: shell ## Alias for 'shell' (interactive shell inside container)

# =============================================================================
# Testing (requires pytest + pytest-cov + pytest-mock)
# These targets prefer the Dev Container's venv when available.
# =============================================================================

PYTEST := $(shell command -v pytest 2>/dev/null || echo python3 -m pytest)

test: ## Run unit tests
	$(PYTEST)

test-cov: ## Run tests with coverage report (HTML report in htmlcov/)
	$(PYTEST) --cov=.devcontainer/scripts --cov-report=term-missing --cov-report=html

test-verbose: ## Run tests with maximum verbosity
	$(PYTEST) -vv

coverage: test-cov ## Alias for test-cov
	@echo "Coverage report generated in htmlcov/"

validate: validate-python lint-shell test ## Run all practical host-side validation (lint + tests)
	@echo "✅ All host-side validation passed."
