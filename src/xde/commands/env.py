"""Environment inspection and management commands."""

from __future__ import annotations

import json
import secrets
from pathlib import Path

from xde.core.docker import DockerComposeController
from xde.core.environment import EnvironmentContext
from xde.utils.output import print_info, print_success, print_warning

ENV_FILE = Path(".devcontainer/.env")
CONFIG_PATH = Path(".devcontainer/create-payload-config.json")

DEFAULT_DB_NAME = "payload_db"
DEFAULT_DB_USER = "payload"


def _load_db_details() -> tuple[str, str]:
    """Load dbName/dbUser from config (pure, matches legacy scripts)."""
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
            pass
    return db_name, db_user


def generate_fresh_env_content() -> str:
    """Pure: return .env content with fresh secrets + db from config.

    Fully testable, no I/O or side effects.
    Adapter-aware for 0.2.0+ (postgres or mongodb).
    """
    db_name, db_user = _load_db_details()
    payload_secret = secrets.token_hex(32)

    # Load adapter to decide env style (default postgres for stability)
    adapter = "postgres"
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open(encoding="utf-8") as f:
                cfg = json.load(f)
            adapter = str(cfg.get("dbAdapter", "postgres")).lower()
        except Exception:
            pass

    if adapter == "mongodb":
        mongo_pass = secrets.token_hex(16)
        return f"""MONGO_INITDB_ROOT_USERNAME={db_user}
MONGO_INITDB_ROOT_PASSWORD={mongo_pass}
MONGO_INITDB_DATABASE={db_name}
PAYLOAD_SECRET={payload_secret}
DATABASE_URI=mongodb://{db_user}:{mongo_pass}@mongodb:27017/{db_name}?authSource=admin
"""
    else:
        # postgres (default)
        pg_pass = secrets.token_hex(16)
        return f"""POSTGRES_USER={db_user}
POSTGRES_PASSWORD={pg_pass}
POSTGRES_DB={db_name}
PAYLOAD_SECRET={payload_secret}
DATABASE_URI=postgres://{db_user}:{pg_pass}@postgres:5432/{db_name}
"""


def perform_env_regenerate(
    *, dry_run: bool = False, yes: bool = False, env_file: Path = ENV_FILE
) -> int:
    """Regenerate .env (fresh creds). Dry-run and yes guard supported."""
    if dry_run:
        content = generate_fresh_env_content()
        print_info("Dry run: would write fresh credentials to .env")
        print_info(f"  (content length: {len(content)} chars)")
        return 0

    if not yes:
        print_warning("This will overwrite .env with new random credentials.")
        print_warning("Re-run with --yes to proceed.")
        return 1

    content = generate_fresh_env_content()
    try:
        with env_file.open("w", encoding="utf-8") as f:
            f.write(content)
        db_name, db_user = _load_db_details()
        adapter = "postgres"
        if CONFIG_PATH.exists():
            try:
                with CONFIG_PATH.open(encoding="utf-8") as f:
                    cfg = json.load(f)
                adapter = str(cfg.get("dbAdapter", "postgres")).lower()
            except Exception:
                pass
        print_success(f"Generated fresh credentials in {env_file}")
        if adapter == "mongodb":
            print_info(f"  (MONGO DB for {db_name})")
        else:
            print_info(f"  (POSTGRES_DB={db_name}, POSTGRES_USER={db_user})")
        return 0
    except Exception as e:
        print_warning(f"Failed to write {env_file}: {e}")
        return 1


def run_env(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Inspect or manage the generated environment."""
    if getattr(args, "regenerate", False):
        dry = getattr(args, "dry_run", False)
        yes = getattr(args, "yes", False)
        return perform_env_regenerate(dry_run=dry, yes=yes)

    use_json = getattr(args, "json", False)

    env_file_exists = ENV_FILE.exists()
    services_ok = docker.services_running()
    payload_project = docker.get_payload_project_name()

    if use_json:
        result = {
            "env_file_exists": env_file_exists,
            "services_running": services_ok,
            "payload_project": payload_project,
            "environment": env.describe(),
        }
        print(json.dumps(result, indent=2))
        return 0
    else:
        print_info("Development environment status:")

        if env_file_exists:
            print_success(f".env file exists at {ENV_FILE}")
        else:
            print_info(
                ".env file not found (run init-env or xde up to generate)"
            )

        if services_ok:
            print_success("Compose services: appear to be running")
        else:
            print_info("Compose services: not detected as running")

        print_info(f"Configured Payload project: {payload_project}")
        print_info("Environment context: " + env.describe())

        return 0
