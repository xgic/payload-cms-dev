#!/bin/bash
#
# .devcontainer/init-env.sh
# XGIC Payload CMS Dev Containers — Host-side .env generation
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.devcontainer/.env"

log()   { echo -e "\033[1;36m[init-env]\033[0m $1"; }
success() { echo -e "\033[1;32m[init-env]\033[0m ✅ $1"; }
warn()  { echo -e "\033[1;33m[init-env]\033[0m ⚠️  $1"; }

if [[ -f "$ENV_FILE" ]]; then
    success ".env already exists — skipping (idempotent)"
    exit 0
fi

log "Generating secure environment configuration..."

read -rp "PostgreSQL admin username [payload]: " POSTGRES_USER
POSTGRES_USER=${POSTGRES_USER:-payload}

read -rp "PostgreSQL admin password (blank = random): " POSTGRES_PASSWORD
if [[ -z "$POSTGRES_PASSWORD" ]]; then
    POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -dc 'A-Za-z0-9!@#%^&*()_+' | head -c 20)
    warn "Generated secure random PostgreSQL password"
fi

read -rp "pgAdmin 4 admin email [${POSTGRES_USER}@example.com]: " PGADMIN_EMAIL
PGADMIN_EMAIL=${PGADMIN_EMAIL:-${POSTGRES_USER}@example.com}

read -rp "pgAdmin 4 admin password (blank = reuse PostgreSQL): " PGADMIN_PASSWORD
PGADMIN_PASSWORD=${PGADMIN_PASSWORD:-$POSTGRES_PASSWORD}

cat > "$ENV_FILE" <<EOF
NODE_ENV=development

POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=payload_db

DATABASE_URI=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/payload_db
PAYLOAD_SECRET=$(openssl rand -base64 32 | tr -d '\n')

PGADMIN_DEFAULT_EMAIL=${PGADMIN_EMAIL}
PGADMIN_DEFAULT_PASSWORD=${PGADMIN_PASSWORD}
EOF

chmod 600 "$ENV_FILE"
success "Generated secure .env at $ENV_FILE"
log "Payload project creation will occur inside the container via postCreateCommand."