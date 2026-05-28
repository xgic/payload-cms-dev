#!/usr/bin/env python3
"""
Dev Container Fast Reset Tool
=============================

Reliable Python implementation of the "fast reset" workflow that
`make reset-project` attempts to perform.

This provides a robust, Python-based implementation of the fast reset
workflow (with support for --compact output used by `make reset-project`).

What it does (the two atomic steps by default):
  1. Delete the generated Payload CMS project folder
  2. Reset only the Postgres service + its named volume (data is destroyed)

Credentials (POSTGRES_PASSWORD, DATABASE_URI, PAYLOAD_SECRET) are intentionally
left unchanged. This avoids the common "stale environment variables in the
running container vs freshly written .env on disk" authentication problems.

For explicit credential rotation, use --rotate-credentials (or do a full
`make clean` + container rebuild).

This is intentionally *not* a full "nuke everything" like `make clean`.
It leaves the main dev container and image alone.

Usage examples:
    # Interactive (recommended on first use)
    python .devcontainer/scripts/reset-project.py

    # Non-interactive (for scripts / CI / automation)
    python .devcontainer/scripts/reset-project.py --yes

    # See exactly what would happen without touching anything
    python .devcontainer/scripts/reset-project.py --dry-run -v

    # Concise output (as produced by 'make reset-project')
    python .devcontainer/scripts/reset-project.py --compact --yes

After a successful run you will normally want to run the Payload
setup automation again (it will use the stable DATABASE_URI):
    - On the host:   make post-create   (or make rebuild for full cycle)
    - Inside container:  bash .devcontainer/scripts/setup-payload.sh

Optional flags:
    --rotate-credentials   Also generate fresh DB password + PAYLOAD_SECRET
                           (only needed when you explicitly want to rotate)

Environment variables respected (for advanced use):
    COMPOSE_FILE, COMPOSE_PROJECT_NAME, ENV_FILE, POSTGRES_VOLUME_NAME,
    LOG_LEVEL, NO_COLOR, TERM
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# =============================================================================
# Constants & Configuration (kept in sync with Makefile + docker-compose.yml)
# =============================================================================

DEFAULT_COMPOSE_FILE = Path(".devcontainer/docker-compose.yml")
DEFAULT_COMPOSE_PROJECT = "xgic-payload-cms-dev-containers"
DEFAULT_ENV_FILE = Path(".devcontainer/.env")
DEFAULT_POSTGRES_VOLUME = "xgic-payload-cms-dev-containers-postgres-data"
DEFAULT_CONFIG_FILE = Path(".devcontainer/create-payload-config.json")
DEFAULT_PROJECT_NAME_FALLBACK = "my-payload-cms"

# Colors (consistent with the rest of the tooling)
USE_COLOR = (
    sys.stdout.isatty()
    and os.environ.get("NO_COLOR") is None
    and os.environ.get("TERM", "") != "dumb"
)

COLORS: Dict[str, str] = {
    "INFO": "\033[36m",      # Cyan
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",     # Red
    "SUCCESS": "\033[32m",   # Green
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
} if USE_COLOR else {k: "" for k in ["INFO", "WARNING", "ERROR", "SUCCESS", "RESET", "BOLD"]}


# =============================================================================
# Logging (consistent with the rest of the Python automation in this repo)
# =============================================================================

class ColoredFormatter:
    """Minimal colored formatter that highlights success markers."""

    def __init__(self, fmt: str = "[%(levelname)s] %(message)s"):
        self.fmt = fmt

    def format(self, level: str, msg: str) -> str:
        color = COLORS.get(level, "")
        reset = COLORS.get("RESET", "")

        if "✅" in msg or "success" in msg.lower():
            msg = f"{COLORS.get('SUCCESS', '')}{msg}{reset}"
        elif level == "ERROR":
            msg = f"{COLORS.get('ERROR', '')}{msg}{reset}"
        elif level == "WARNING":
            msg = f"{COLORS.get('WARNING', '')}{msg}{reset}"

        level_str = f"{color}{level}{reset}" if color else level
        return f"[{level_str}] {msg}"


log = ColoredFormatter()


def log_info(msg: str) -> None:
    print(log.format("INFO", msg))


def log_success(msg: str) -> None:
    print(log.format("SUCCESS", msg))


def log_warn(msg: str) -> None:
    print(log.format("WARNING", msg), file=sys.stderr)


def log_error(msg: str) -> None:
    print(log.format("ERROR", msg), file=sys.stderr)


def log_step(step_num: int, total: int, action: str) -> None:
    """Print a nicely formatted step header."""
    prefix = f"{COLORS.get('BOLD', '')}Step {step_num}/{total}{COLORS.get('RESET', '')}"
    print(f"{prefix}  {action}")


# =============================================================================
# Helper Functions
# =============================================================================

def is_running_in_devcontainer() -> bool:
    """Detect whether we are executing inside a VS Code Dev Container."""
    if os.environ.get("REMOTE_CONTAINERS") == "true":
        return True
    if os.environ.get("CODESPACES") == "true":
        return True
    # Additional heuristic: the specific hostname pattern used by the container
    if os.environ.get("XG_AIS_HOST_TYPE") == "xgic-devcontainer":
        return True
    return False


def get_payload_project_name(config_path: Path = DEFAULT_CONFIG_FILE) -> str:
    """
    Return the name of the generated Payload project folder.

    Mirrors the logic in get-payload-project-name.py so we stay in sync
    with the single source of truth (create-payload-config.json).
    """
    if not config_path.exists():
        return DEFAULT_PROJECT_NAME_FALLBACK

    try:
        with config_path.open(encoding="utf-8") as f:
            data = json.load(f)
        name = data.get("projectName")
        if name and isinstance(name, str) and name.strip():
            return name.strip()
    except Exception as exc:
        log_warn(f"Could not read projectName from {config_path}: {exc}")

    return DEFAULT_PROJECT_NAME_FALLBACK


def find_payload_project_dirs(workspace: Path) -> list[Path]:
    """Find directories that look like they contain a Payload CMS project.

    Handles both the classic layout (config at root) and the template layout
    used by this repository (config inside src/).
    """
    candidates: list[Path] = []
    for entry in workspace.iterdir():
        if not entry.is_dir() or entry.name.startswith("."):
            continue

        # Classic location
        if (entry / "payload.config.ts").exists() or (entry / "payload.config.js").exists():
            candidates.append(entry)
            continue

        # Template layout used in this repo (config lives in src/)
        if (entry / "src" / "payload.config.ts").exists() or (entry / "src" / "payload.config.js").exists():
            candidates.append(entry)
            continue

        # Fallback heuristic via package.json
        pkg = entry / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if any("payload" in k.lower() for k in deps):
                    candidates.append(entry)
            except Exception:
                pass
    return sorted(candidates)


def run(cmd: list[str], *, dry_run: bool = False, check: bool = True,
        capture_output: bool = True, **kwargs: Any) -> subprocess.CompletedProcess[str]:
    """
    Run a subprocess command with good defaults and clear error reporting.
    """
    if dry_run:
        print(f"    $ {' '.join(cmd)}")
        # Return a fake successful result for dry-run
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    try:
        return subprocess.run(
            cmd,
            check=check,
            text=True,
            capture_output=capture_output,
            **kwargs,
        )
    except subprocess.CalledProcessError as e:
        log_error(f"Command failed: {' '.join(cmd)}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        raise


def delete_project_folder(project_name: str, workspace: Path, *, dry_run: bool = False, quiet: bool = False) -> bool:
    """Remove the generated Payload project directory if it exists."""
    target = workspace / project_name

    if not target.exists():
        if not quiet:
            log_info(f"Project folder '{project_name}' does not exist at {target} — nothing to delete.")
        return True

    if not quiet:
        log_info(f"Removing generated project folder: {target}")

    if dry_run:
        if not quiet:
            print(f"    (would run: rm -rf {target})")
        return True

    try:
        shutil.rmtree(target)
        if not quiet:
            log_success(f"Deleted {target}")
        return True
    except Exception as exc:
        if not quiet:
            log_error(f"Failed to delete {target}: {exc}")
        return False


def regenerate_credentials(
    env_file: Path,
    init_script: Path,
    *,
    dry_run: bool = False,
    quiet: bool = False,
) -> bool:
    """Regenerate .devcontainer/.env with fresh secure credentials."""
    if not quiet:
        log_info("Regenerating fresh database credentials (.env)")

    if dry_run:
        if not quiet:
            print(f"    (would run: python3 .devcontainer/scripts/regenerate-env.py)")
        return True

    # Preferred: pure Python implementation
    regen_py = Path(".devcontainer/scripts/regenerate-env.py")
    if regen_py.exists():
        try:
            run([sys.executable, str(regen_py)], dry_run=False, check=True)
            if not quiet:
                log_success("Fresh credentials written by regenerate-env.py")
            return True
        except subprocess.CalledProcessError:
            if not quiet:
                log_warn("Python credential regeneration failed — trying Bash fallback...")

    # Fallback: the original Bash script
    if init_script.exists():
        try:
            run(["bash", str(init_script)], dry_run=False, check=True)
            if not quiet:
                log_success("Fresh credentials written by init-env.sh (fallback)")
            return True
        except subprocess.CalledProcessError:
            if not quiet:
                log_error("Both Python and Bash credential regeneration failed.")
            return False

    if not quiet:
        log_error("No credential regeneration method available.")
    return False


def _get_db_details_from_config(config_path: Path) -> tuple[str, str]:
    """Return (db_name, db_user) preferring explicit fields in the config,
    with fallback to parsing the dbUri.
    """
    default_db = "payload_db"
    default_user = "payload"

    if not config_path.exists():
        return default_db, default_user

    try:
        with config_path.open(encoding="utf-8") as f:
            cfg = json.load(f)

        db_name = cfg.get("dbName")
        db_user = cfg.get("dbUser")

        # Fallback: parse from dbUri
        db_uri = cfg.get("dbUri") or ""
        if db_uri and (not db_name or not db_user):
            try:
                if "://" in db_uri:
                    after_scheme = db_uri.split("://", 1)[1]
                    # user:pass@host...
                    if "@" in after_scheme:
                        creds_part = after_scheme.split("@", 1)[0]
                        if ":" in creds_part and not db_user:
                            db_user = creds_part.split(":", 1)[0]
                    # .../dbname
                    if "/" in after_scheme:
                        after_host = after_scheme.split("@", 1)[-1]
                        path = after_host.split("/", 1)[-1].split("?")[0]
                        if path and not db_name:
                            db_name = path
            except Exception:
                pass

        return (db_name or default_db, db_user or default_user)

    except Exception:
        return default_db, default_user


def reset_postgres(
    compose_file: Path,
    project_name: str,
    volume_name: str,
    *,
    config_path: Path,
    dry_run: bool = False,
    quiet: bool = False,
) -> bool:
    """Reset only the Postgres service and its data volume."""
    if not quiet:
        log_info("Resetting Postgres service + named data volume")

    base_cmd = [
        "docker", "compose",
        "-f", str(compose_file),
        "-p", project_name,
    ]

    if dry_run:
        if not quiet:
            print(f"    $ {' '.join(base_cmd)} rm -f -s -v postgres")
            print(f"    $ docker volume rm {volume_name}")
            print(f"    $ {' '.join(base_cmd)} up -d postgres")
        return True

    # 1. Stop and remove the postgres container (with its volumes)
    try:
        run(base_cmd + ["rm", "-f", "-s", "-v", "postgres"],
            check=False, capture_output=True)
    except Exception:
        pass  # Best effort — container may already be gone

    # 2. Remove the named volume (this is the destructive part)
    try:
        run(["docker", "volume", "rm", volume_name], check=False)
    except Exception:
        pass

    # 3. Bring the postgres service back up + ensure app database exists
    try:
        run(base_cmd + ["up", "-d", "postgres"], check=True)
        if not quiet:
            log_success("Postgres service recreated with fresh volume")

        db_name, db_user = _get_db_details_from_config(config_path)

        # Give Postgres a moment to accept connections
        for _ in range(25):
            res = run(
                base_cmd + [
                    "exec", "-T", "postgres",
                    "pg_isready", "-U", db_user, "-h", "127.0.0.1"
                ],
                check=False,
                capture_output=True,
            )
            if res.returncode == 0:
                break
            import time
            time.sleep(1)

        # Create the database if it doesn't exist (idempotent)
        run(
            base_cmd + [
                "exec", "-T", "postgres",
                "psql", "-U", db_user, "-d", "postgres", "-h", "127.0.0.1",
                "-c", f"CREATE DATABASE {db_name} OWNER {db_user};"
            ],
            check=False,
            capture_output=True,
        )
        if not quiet:
            log_success(f"Ensured database '{db_name}' exists")

        return True

    except subprocess.CalledProcessError:
        if not quiet:
            log_error("Failed to start Postgres after volume reset.")
            log_error("You may need to run the command manually from the host:")
            log_error(f"    docker compose -f {compose_file} -p {project_name} up -d postgres")
        return False


# =============================================================================
# Main Flow
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fast, reliable reset of Payload project + Postgres (dev container safe).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-y", "--yes", "--force",
        dest="assume_yes",
        action="store_true",
        help="Skip the confirmation prompt (non-interactive use).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show exactly what would be done without making any changes.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable more detailed output (sets LOG_LEVEL=DEBUG internally if needed).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_FILE,
        help="Path to create-payload-config.json (source of truth for project name).",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace root (normally the repository root).",
    )
    parser.add_argument(
        "--project-name",
        type=str,
        default=None,
        help="Override the Payload project folder name (bypasses create-payload-config.json).",
    )
    parser.add_argument(
        "--rotate-credentials", "--rotate-creds",
        dest="rotate_credentials",
        action="store_true",
        help="Also regenerate the database password and PAYLOAD_SECRET (not recommended for normal fast resets).",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Produce concise one-line-per-task output with ✅/❌ (used by 'make reset-project').",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"

    compact = args.compact
    in_container = is_running_in_devcontainer()

    # Common setup (needed by both rich and compact modes)
    configured_name = get_payload_project_name(args.config)
    project_name = args.project_name or configured_name

    compose_file = Path(os.environ.get("COMPOSE_FILE", DEFAULT_COMPOSE_FILE))
    compose_project = os.environ.get("COMPOSE_PROJECT_NAME", DEFAULT_COMPOSE_PROJECT)
    env_file = Path(os.environ.get("ENV_FILE", DEFAULT_ENV_FILE))
    postgres_volume = os.environ.get("POSTGRES_VOLUME_NAME", DEFAULT_POSTGRES_VOLUME)
    init_script = Path(".devcontainer/scripts/init-env.sh")

    if not compact:
        container_note = " (inside dev container)" if in_container else ""
        print(f"\n{COLORS.get('BOLD', '')}XGIC Payload CMS — Fast Project Reset{container_note}{COLORS.get('RESET', '')}")
        print("This will perform a *targeted* reset (project folder + Postgres volume).")
        if args.rotate_credentials:
            print("Credential rotation requested via --rotate-credentials.")
        else:
            print("Database credentials are left unchanged (recommended for fast resets).")
        print("The main dev container and its image are left untouched.\n")

        # Smart detection for project folder mismatches (very common during development)
        target = args.workspace / project_name
        all_payload_dirs = find_payload_project_dirs(args.workspace)
        other_projects = [p for p in all_payload_dirs if p.name != project_name]

        print("Planned actions:")
        print(f"  • Delete generated Payload folder: {project_name}/")
        if other_projects:
            if target.exists():
                log_info(f"Other Payload project directories also present: {[p.name for p in other_projects]}")
            else:
                log_warn("The configured project folder does not exist on disk.")
                log_warn(f"Other Payload-looking directories found: {[p.name for p in other_projects]}")
                log_warn("If this is the wrong folder, re-run with: --project-name <correct-name>")
        elif not target.exists():
            log_warn(f"Configured project folder '{project_name}' not found and no other Payload projects detected.")

        if args.rotate_credentials:
            print(f"  • Regenerate fresh credentials in {env_file}  (⚠️  --rotate-credentials)")
        print(f"  • Reset Postgres service + volume: {postgres_volume}")
        print()

    # ============================================================
    # Brief developer warnings (compact mode) — shown before the confirmation prompt
    # ============================================================
    if compact:
        print("⚠️  This will delete the generated Payload project folder and reset the Postgres database.")
        print()

    if not args.assume_yes and not args.dry_run:
        try:
            answer = input("Type 'yes' to continue (anything else cancels): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Cancelled.")
            return 1

        if answer != "yes":
            print("❌ Operation cancelled by user.")
            return 1
    elif args.dry_run and not compact:
        log_warn("DRY RUN — no changes will be made.\n")

    # ============================================================
    # Execute major tasks
    # ============================================================
    green = COLORS.get("SUCCESS", "")
    red   = COLORS.get("ERROR", "")
    resetc = COLORS.get("RESET", "")   # "reset" is a builtin

    overall_success = True

    # --- Task 1: Delete generated Payload project folder ---
    if compact:
        print("  Deleting generated project folder... ", end="", flush=True)
    else:
        log_step(1, 2 + (1 if args.rotate_credentials else 0), "Delete generated Payload project folder")

    ok = delete_project_folder(project_name, args.workspace, dry_run=args.dry_run, quiet=compact)
    if compact:
        print(f"{green}✅{resetc}" if ok else f"{red}❌{resetc}")
    if not ok:
        overall_success = False

    # --- Task 2: Regenerate credentials (only when explicitly requested) ---
    if args.rotate_credentials:
        if compact:
            print("  Regenerating database credentials... ", end="", flush=True)
        else:
            log_step(2, 3, "Regenerate fresh database credentials (explicit --rotate-credentials)")

        ok = regenerate_credentials(env_file, init_script, dry_run=args.dry_run, quiet=compact)
        if compact:
            print(f"{green}✅{resetc}" if ok else f"{red}❌{resetc}")
        if not ok:
            overall_success = False

    # --- Task 3: Reset Postgres service + volume ---
    task_num = 2 if not args.rotate_credentials else 3
    if compact:
        print("  Resetting Postgres service + volume... ", end="", flush=True)
    else:
        log_step(task_num, task_num, "Reset Postgres service and data volume")

    ok = reset_postgres(
        compose_file,
        compose_project,
        postgres_volume,
        config_path=args.config,
        dry_run=args.dry_run,
        quiet=compact,
    )
    if compact:
        print(f"{green}✅{resetc}" if ok else f"{red}❌{resetc}")
    if not ok:
        overall_success = False

    # ============================================================
    # Final reporting
    # ============================================================
    if compact:
        print()
        if overall_success:
            print(f"{green}✅ Reset complete.{resetc}")
        else:
            print(f"{red}❌ Reset failed.{resetc}")
        return 0 if overall_success else 1
    else:
        # Rich reporting (original behavior)
        print()
        if overall_success:
            if args.rotate_credentials:
                log_success("Project and database reset complete (credentials rotated).")
            else:
                log_success("Project and database reset complete (credentials left stable).")
            print()

            if args.dry_run:
                print("Dry run finished. Re-run without --dry-run to execute.")
                return 0

            # Context-aware next steps
            print("Next steps:")
            if in_container:
                print("  Inside the container you can now run:")
                print("      bash .devcontainer/scripts/setup-payload.sh")
                print("  (This uses create-payload-config.json for fully non-interactive creation.)")
            else:
                print("  On the host, the recommended command is usually:")
                print("      make post-create")
                print("  or for a full clean rebuild:")
                print("      make rebuild")
            print()
            return 0
        else:
            log_error("Reset completed with errors. Review the output above.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
