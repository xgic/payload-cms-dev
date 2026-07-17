#!/usr/bin/env bash
# Idempotent Payload CMS project ensure (postStart).
# Canonical implementation: modular XGIC CLI (`xgic payload setup`).
set -euo pipefail
exec xgic payload setup
