#!/bin/bash
#
# - Test VS Code Dev Container.
# 
set -e

readonly SCRIPT_NAME="${0##*/}"

printf "\nStarting ${SCRIPT_NAME} script...\n"
printf "\n$(date)\n"

printf "\nCheck Node.js version.\n"
node --version

printf "\nCheck pnpm version.\n"
pnpm --version

printf "\nCheck PostgreSQL Client version.\n"
psql --version

printf "\nCheck PostgreSQL database access.\n"
psql -h postgres -U payload -d payload_db -c "\l"

printf "\n\nEnding ${SCRIPT_NAME} script...\n"
printf "\n$(date)\n"
