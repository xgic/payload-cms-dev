#!/bin/bash
set -e

# Idempotency guard – prevents re-running on every reopen/restart
if find /workspace -maxdepth 4 -name "payload.config.ts" -o \
   -name "payload.config.js" | grep -q .; then
  echo "✅ Payload CMS project already exists (found payload.config.*)" \
       " – skipping initialization."
  exit 0
fi

printf "\nStarting devcontainer-tests.sh script...\n"
printf "\n$(date)\n"

echo "Check Node.js version."
node --version

echo "Check pnpm version."
pnpm --version

echo "Check PostgreSQL Client version."
psql --version

echo "Check PostgreSQL database access."
PGPASSWORD=${POSTGRES_PASSWORD} psql -U "${POSTGRES_USER}" \
  -d payload_db -c "\l" --no-password

echo "Check Docker CLI (best practice test)."
docker --version
docker info --format "Docker Engine: {{.ServerVersion}}"

echo ""
echo "Ending devcontainer-tests.sh script..."
printf "\n$(date)\n"