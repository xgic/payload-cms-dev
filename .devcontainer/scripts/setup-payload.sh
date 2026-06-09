#!/usr/bin/env bash
set -e

# Thin fail-fast shim for the devcontainer postStartCommand.
#
# All real logic now lives in `xde setup payloadcms` (which calls the
# modular implementation in xde.core.project). This keeps the hook
# minimal and makes `xde` the single source of truth.
#
# The script intentionally has no fallback, no || true, and no "best
# effort continue" behavior: if xde is not in PATH or the setup step
# fails hard, the container startup will surface the failure (as
# requested for reliability and early detection).
exec xde setup payloadcms
