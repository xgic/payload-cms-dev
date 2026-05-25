#!/bin/bash
set -e

# Idempotency guard – prevents re-running on every reopen/restart
if find /workspace -maxdepth 4 -name "payload.config.ts" -o \
   -name "payload.config.js" | grep -q .; then
  echo "✅ Payload CMS project already exists (found payload.config.*)" \
       " – skipping initialization."
  exit 0
fi

echo "[init-env] Generating secure environment configuration..."

# PostgreSQL (non-interactive via env vars with sensible defaults)
PG_USER=${PG_USER:-payload}
PG_PASSWORD=${PG_PASSWORD:-$(openssl rand -hex 16)}

# Payload CMS
PAYLOAD_SECRET=${PAYLOAD_SECRET:-$(openssl rand -hex 32)}

cat > .devcontainer/.env << EOF
POSTGRES_USER=${PG_USER}
POSTGRES_PASSWORD=${PG_PASSWORD}
PAYLOAD_SECRET=${PAYLOAD_SECRET}
DATABASE_URI=postgres://${PG_USER}:${PG_PASSWORD}@postgres:5432/payload_db
EOF

echo "[init-env] ✅ Generated secure .env at $(pwd)/.devcontainer/.env"
echo "[init-env] Payload project creation will occur inside the container" \
     "via postCreateCommand."
