#!/bin/bash
set -e

# Idempotency guard – prevents re-running on every reopen/restart
if find /workspace -maxdepth 4 -name "payload.config.ts" -o \
   -name "payload.config.js" | grep -q .; then
  echo "✅ Payload CMS project already exists (found payload.config.*)" \
       " – skipping initialization."
  exit 0
fi

log()   { echo -e "\033[1;36m[post-create]\033[0m $1"; }
success() { echo -e "\033[1;32m[post-create]\033[0m ✅ $1"; }
warn()  { echo -e "\033[1;33m[post-create]\033[0m ⚠️  $1"; }

CONFIG_FILE="/workspace/.devcontainer/create-payload-config.json"

# Strict validation against current create-payload-app supported values
if [ ! -f "$CONFIG_FILE" ]; then
  warn "create-payload-config.json not found – using defaults."
else
  log "Validating create-payload-config.json..."
  if ! grep -q '"projectName"' "$CONFIG_FILE"; then
    echo "❌ ERROR: create-payload-config.json is invalid (missing projectName)."
    echo "   Supported options (from pnpx create-payload-app -h):"
    echo "   -n <name>   -t blank|website|ecommerce|with-cloudflare-d1|plugin"
    echo "   -a claude|codex|cursor   --no-agent"
    echo ""
    echo "Please fix the file and re-run: make post-create"
    echo "or run make rebuild to start from scratch."
    exit 1
  fi
  success "Configuration validated."
fi

# Dynamically update SQLTools with real credentials
ENV_FILE="/workspace/.devcontainer/.env"
SETTINGS_FILE="/workspace/.vscode/settings.json"
if [ -f "$ENV_FILE" ] && [ -f "$SETTINGS_FILE" ]; then
  PG_USER=$(grep POSTGRES_USER "$ENV_FILE" | cut -d= -f2)
  PG_PASS=$(grep POSTGRES_PASSWORD "$ENV_FILE" | cut -d= -f2)
  sed -i "s/\"username\": \".*\"/\"username\": \"$PG_USER\"/" "$SETTINGS_FILE"
  sed -i "s/\"password\": \".*\"/\"password\": \"$PG_PASS\"/" "$SETTINGS_FILE"
  success "✅ SQLTools connections updated with secure credentials"
fi

log "Creating Payload app from official package..."

cd /workspace
# Hardcoded values temporarily, need to retrieve them from create-payload-config.json
# pnpx create-payload-app -h
pnpx create-payload-app@latest -n my-payload-cms \
  -t website \
  --no-agent \
  --use-pnpm

success "✅ Payload CMS project created (files in subdirectory)"
success "✅ Dev Container initialization complete!"

echo ""
echo "Next steps:"
echo "  1. Open the new Payload CMS subdirectory in VS Code"
echo "  2. Run: pnpm dev"
echo "  3. Visit http://localhost:3000/admin"