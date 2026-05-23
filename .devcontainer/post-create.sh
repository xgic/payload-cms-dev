#!/bin/bash
#
# .devcontainer/post-create.sh
# XGIC Payload CMS Dev Containers — Post-container creation logic
# Runs inside the container (pnpm/npx available)
#
set -euo pipefail

log()   { echo -e "\033[1;36m[post-create]\033[0m $1"; }
success() { echo -e "\033[1;32m[post-create]\033[0m ✅ $1"; }
warn()  { echo -e "\033[1;33m[post-create]\033[0m ⚠️  $1"; }

# 1. Run environment validation tests first
if [[ -x ".devcontainer/devcontainer-tests.sh" ]]; then
    log "Running environment validation tests..."
    ./.devcontainer/devcontainer-tests.sh || warn "Some tests reported issues — continuing"
fi

# 2. Interactive vs Non-Interactive Detection
if [[ -t 0 ]]; then
    INTERACTIVE=true
    log "Interactive terminal detected — launching official Payload CMS wizard"
else
    INTERACTIVE=false
    log "Non-interactive environment (CI/CD) — using .devcontainer/create-payload-config.json"
fi

# 3. Create Payload CMS project
if [[ ! -f "payload.config.ts" && ! -f "src/payload.config.ts" ]]; then
    if [[ "$INTERACTIVE" == "true" ]]; then
        # Full official interactive wizard (no custom prompts or arguments)
        log "Launching official Payload CMS interactive project creation wizard..."
        pnpx create-payload-app@latest
        success "Payload CMS project created interactively (files in subdirectory)"
    else
        # Non-interactive path using comprehensive config (all official parameters)
        log "Creating Payload CMS project from configuration (non-interactive)..."
        CONFIG_FILE=".devcontainer/create-payload-config.json"
        
        # Default values if config is missing
        PROJECT_NAME="payload-cms-app"
        TEMPLATE="blank"
        YES_FLAG="--yes"
        
        if [[ -f "$CONFIG_FILE" ]]; then
            # Parse with jq (fallback if jq missing)
            if command -v jq &> /dev/null; then
                PROJECT_NAME=$(jq -r '.projectName // "payload-cms-app"' "$CONFIG_FILE")
                TEMPLATE=$(jq -r '.template // "blank"' "$CONFIG_FILE")
                YES_FLAG=$(jq -r 'if .yes == true then "--yes" else "" end' "$CONFIG_FILE")
            fi
        fi
        
        pnpx create-payload-app@latest "$PROJECT_NAME" --template "$TEMPLATE" $YES_FLAG
        success "Payload CMS project created non-interactively"
    fi
else
    log "Payload project already exists — skipping creation"
fi

success "✅ Dev Container initialization complete!"
echo ""
echo "Next steps:"
echo "  1. Open the new Payload CMS subdirectory in VS Code (or cd into it)"
echo "  2. Run: pnpm dev"
echo "  3. Visit http://localhost:3000/admin"
echo "  4. pgAdmin available at http://localhost:8080"
echo ""
echo "For non-interactive automation, customize .devcontainer/create-payload-config.json"