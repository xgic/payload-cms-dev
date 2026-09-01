#!/usr/bin/env python3
"""Write libpq exports from create-payload-config.json (not hardcoded names).

``POSTGRES_DB`` is only for the official Postgres image init. libpq reads
``PGDATABASE`` / ``PGUSER``. Values come from the live workspace config:

  .devcontainer/create-payload-config.json  (dbName, dbUser)

``.devcontainer/config/`` is the schema/types source, not the live JSON.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

DEFAULT_CONFIG = Path("/workspace/.devcontainer/create-payload-config.json")
DEFAULT_PROFILE = Path("/etc/profile.d/xgic-libpq.sh")
PGHOST = "postgres"  # Compose service key (consumer-contract exemplar)


def _safe_ident(value: str) -> str | None:
    value = value.strip()
    if not value or not _IDENT.fullmatch(value):
        return None
    return value


def libpq_exports(config_path: Path) -> str | None:
    """Return profile.d text from *config_path*, or None if unusable."""
    if not config_path.is_file():
        return None
    try:
        from xgic.cli.payload.config import get_db_config
    except ImportError:
        return None
    db_name, db_user = get_db_config(config_path)
    db_name_s = _safe_ident(str(db_name))
    db_user_s = _safe_ident(str(db_user))
    if not db_name_s or not db_user_s:
        return None
    return (
        "# Generated from create-payload-config.json (dbName / dbUser).\n"
        f"export PGHOST={PGHOST}\n"
        f"export PGUSER={db_user_s}\n"
        f"export PGDATABASE={db_name_s}\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_PROFILE)
    args = parser.parse_args(argv)
    text = libpq_exports(args.config)
    if not text:
        return 0
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        args.output.chmod(0o644)
    except OSError:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
