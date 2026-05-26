#!/usr/bin/env python3
"""Regenerate .devcontainer/.env with fresh secure credentials.

This is primarily used for:
- Initial dev container creation (via init-env.sh)
- Explicit credential rotation (via --rotate-credentials on the reset script,
  or calling this directly / make env-regenerate)

Database name and user are read from .devcontainer/create-payload-config.json
when available (fields: dbName, dbUser), falling back to sensible defaults.
"""

import json
import os
import secrets
import sys
from pathlib import Path

ENV_PATH = Path(".devcontainer/.env")
CONFIG_PATH = Path(".devcontainer/create-payload-config.json")

# Defaults
DEFAULT_DB_NAME = "payload_db"
DEFAULT_DB_USER = "payload"

def _load_db_details() -> tuple[str, str]:
    """Load dbName and dbUser from config, with safe fallbacks."""
    db_name = DEFAULT_DB_NAME
    db_user = DEFAULT_DB_USER

    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open(encoding="utf-8") as f:
                cfg = json.load(f)
            if cfg.get("dbName"):
                db_name = cfg["dbName"]
            if cfg.get("dbUser"):
                db_user = cfg["dbUser"]
        except Exception:
            pass  # fall back to defaults on any error

    return db_name, db_user


# Allow override via environment for advanced use
PG_USER = os.environ.get("PG_USER") or _load_db_details()[1]
PG_PASSWORD = os.environ.get("PG_PASSWORD") or secrets.token_hex(16)
PAYLOAD_SECRET = os.environ.get("PAYLOAD_SECRET") or secrets.token_hex(32)

DB_NAME, DB_USER = _load_db_details()

# Re-derive user if env override was used
if os.environ.get("PG_USER"):
    DB_USER = PG_USER

content = f"""POSTGRES_USER={PG_USER}
POSTGRES_PASSWORD={PG_PASSWORD}
POSTGRES_DB={DB_NAME}
PAYLOAD_SECRET={PAYLOAD_SECRET}
DATABASE_URI=postgres://{PG_USER}:{PG_PASSWORD}@postgres:5432/{DB_NAME}
"""

try:
    with ENV_PATH.open("w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Generated fresh credentials in {ENV_PATH}")
    print(f"  (POSTGRES_DB={DB_NAME}, new random POSTGRES_PASSWORD + matching DATABASE_URI)")
except Exception as e:
    print(f"ERROR: Failed to write {ENV_PATH}: {e}", file=sys.stderr)
    sys.exit(1)
