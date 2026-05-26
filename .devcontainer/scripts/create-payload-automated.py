#!/usr/bin/env python3
"""
Payload CMS Interactive Automation Script
=========================================
Automates `pnpx create-payload-app@latest` using pexpect for the
interactive portions of the wizard (database selection, connection string, etc.).

Features:
- Accepts configuration via JSON file (create-payload-config.json) or CLI flags.
- Uses pexpect + PTY for reliable arrow-key and prompt handling.
- Robust prompt matching using regex + detailed diagnostics on failure.
- Designed for VS Code Dev Containers (called from thin bash wrappers).

Usage examples:
    python .devcontainer/scripts/create-payload-automated.py
    python .devcontainer/scripts/create-payload-automated.py --config .devcontainer/create-payload-config.json
    python .devcontainer/scripts/create-payload-automated.py --name my-app --template website
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pexpect

# Simple color support (no external dependencies)
USE_COLOR = (
    sys.stdout.isatty()
    and os.environ.get("NO_COLOR") is None
    and os.environ.get("TERM", "") != "dumb"
)

COLORS = {
    "INFO": "\033[36m",      # Cyan
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",     # Red
    "SUCCESS": "\033[32m",   # Green
    "RESET": "\033[0m",
} if USE_COLOR else {k: "" for k in ["INFO", "WARNING", "ERROR", "SUCCESS", "RESET"]}

# =============================================================================
# Configuration & Constants
# =============================================================================

DEFAULT_CONFIG: Dict[str, Any] = {
    "projectName": "my-payload-cms",
    "template": "website",
    "agent": "--no-agent",
    "dbAdapter": "postgres",
    "dbUri": None,                    # Will be read from DATABASE_URI env if not provided
    "usePnpm": True,
}

# pexpect constants (as strings because we spawn with encoding="utf-8")
TIMEOUT_SECONDS = 180
DOWN_ARROW = "\x1b[B"
ENTER = "\r"
CTRL_U = "\x15"

# Expected prompt fragments (from create-payload-app wizard)
# Using regex patterns (str, not bytes) for robustness against ANSI codes, box characters, etc.
PROMPT_DB_SELECT = re.compile(r".*?Select a database", re.IGNORECASE)
PROMPT_POSTGRES_SELECTED = re.compile(r".*?PostgreSQL", re.IGNORECASE)
PROMPT_CONNECTION_STRING = re.compile(r".*?Enter (?:your )?PostgreSQL connection string", re.IGNORECASE)

# Configure logging level from environment (default INFO)
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="[%(levelname)s] %(message)s",
)

# Custom logger with color support for key levels
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname
        color = COLORS.get(level, "")
        reset = COLORS.get("RESET", "")

        # Color the level name
        colored_level = f"{color}{level}{reset}" if color else level

        # Color success messages
        msg = record.getMessage()
        if "✅" in msg:
            msg = f"{COLORS.get('SUCCESS', '')}{msg}{reset}"

        # Reconstruct the formatted message
        record.levelname = colored_level
        record.msg = msg
        record.args = ()
        return super().format(record)

# Reconfigure root logger with color support
for handler in logging.root.handlers:
    handler.setFormatter(ColoredFormatter("[%(levelname)s] %(message)s"))

log = logging.getLogger(__name__)


# =============================================================================
# Config Loading & CLI
# =============================================================================

def load_config(config_path: Optional[Path]) -> Dict[str, Any]:
    """Load configuration from JSON file, falling back to defaults."""
    config = DEFAULT_CONFIG.copy()

    if config_path and config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as f:
                file_config = json.load(f)
            config.update(file_config)
            log.info(f"Loaded configuration from {config_path}")
        except Exception as exc:
            log.warning(f"Failed to load config file {config_path}: {exc}")
    else:
        if config_path:
            log.warning(f"Config file not found: {config_path} — using defaults + CLI/env")

    # DATABASE_URI from the environment (injected by docker-compose) should take
    # precedence over the value in create-payload-config.json. This is the "live"
    # connection string for the running postgres service.
    env_db_uri = os.getenv("DATABASE_URI")
    if env_db_uri:
        # Only use it if it looks like a real URI (defensive against "undefined" strings
        # that can sometimes appear from variable expansion in devcontainer setups)
        if env_db_uri and env_db_uri.lower() != "undefined" and "://" in env_db_uri:
            config["dbUri"] = env_db_uri
        else:
            log.warning(f"DATABASE_URI from environment looks invalid ('{env_db_uri}'), ignoring it.")

    # Final safety check
    final_db_uri = config.get("dbUri")
    if final_db_uri and (final_db_uri.lower() == "undefined" or not final_db_uri.strip()):
        log.warning("dbUri resolved to an invalid/undefined value. Clearing it.")
        config["dbUri"] = None

    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automate Payload CMS project creation with pexpect.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path(".devcontainer/create-payload-config.json"),
        help="Path to create-payload-config.json",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory in which to run create-payload-app",
    )
    parser.add_argument("-n", "--name", help="Project name (overrides config)")
    parser.add_argument("-t", "--template", help="Template (website, blank, ecommerce, ...)")
    parser.add_argument("--db-adapter", choices=["postgres", "mongodb", "sqlite"], help="Database adapter")
    parser.add_argument("--db-uri", help="Database connection string (overrides env and config)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without executing the wizard",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

    return parser.parse_args()


def merge_config(args: argparse.Namespace, file_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge CLI arguments over file config (CLI wins)."""
    cfg = file_config.copy()

    if args.name:
        cfg["projectName"] = args.name
    if args.template:
        cfg["template"] = args.template
    if args.db_adapter:
        cfg["dbAdapter"] = args.db_adapter
    if args.db_uri:
        cfg["dbUri"] = args.db_uri

    return cfg


def build_command(cfg: Dict[str, Any]) -> list[str]:
    """Construct the initial command line for create-payload-app."""
    cmd = ["pnpx", "create-payload-app@latest"]

    if cfg.get("projectName"):
        cmd += ["-n", str(cfg["projectName"])]
    if cfg.get("template"):
        cmd += ["-t", str(cfg["template"])]
    if cfg.get("agent"):
        cmd += [str(cfg["agent"])]
    if cfg.get("usePnpm") or cfg.get("use-pnpm"):
        cmd += ["--use-pnpm"]

    return cmd


# =============================================================================
# Core Automation Logic (pexpect)
# =============================================================================

def _project_has_payload_config(project_dir: Path) -> bool:
    """Check if a Payload project already exists in the target directory."""
    for name in ("payload.config.ts", "payload.config.js"):
        if (project_dir / name).exists():
            return True
    # Also check one level deep (common when project is created in a subdir)
    for name in ("payload.config.ts", "payload.config.js"):
        if any((project_dir / subdir / name).exists() for subdir in project_dir.iterdir() if subdir.is_dir()):
            return True
    return False


def _log_pexpect_context(child: "pexpect.spawn", reason: str) -> None:
    """Log detailed context when pexpect encounters a timeout or EOF."""
    log.error(f"pexpect failure reason: {reason}")
    if child is None:
        log.error("No pexpect child process available for diagnostics.")
        return
    try:
        before = getattr(child, "before", None) or ""
        after = getattr(child, "after", None) or ""
        # In text mode (with encoding), before/after are already str
        log.error("Last output before failure (last 800 chars):\n%s", before[-800:] if isinstance(before, str) else before[-800:].decode("utf-8", errors="replace"))
        if after:
            after_str = after if isinstance(after, str) else after.decode("utf-8", errors="replace")
            log.error("Output after last match:\n%s", after_str)
    except Exception as e:
        log.error("Failed to extract pexpect buffer: %s", e)


def run_payload_wizard(
    cfg: Dict[str, Any],
    project_dir: Path,
    dry_run: bool = False,
    *,
    spawn: callable = None,
) -> None:
    """
    Run the interactive create-payload-app wizard with pexpect automation.

    The `spawn` parameter is primarily intended for testing. In normal use it
    defaults to pexpect.spawn.
    """
    if spawn is None:
        spawn = pexpect.spawn

    # Idempotency check (authoritative version)
    if _project_has_payload_config(project_dir):
        log.info("✅ Payload CMS project already exists (found payload.config.*) — skipping creation.")
        return

    database_uri: Optional[str] = cfg.get("dbUri")
    if not database_uri or database_uri.lower() == "undefined":
        log.error(
            "No valid DATABASE_URI found. "
            "Make sure the .env file (generated by init-env.sh) is loaded by docker-compose, "
            "or pass --db-uri on the command line."
        )
        sys.exit(1)

    command = build_command(cfg)
    log.info(f"Project directory: {project_dir}")
    log.info(f"Running: {' '.join(command)}")

    if dry_run:
        log.info("[DRY RUN] Would execute the wizard with the above command and pexpect automation.")
        return

    # Ensure we run in the correct directory
    original_cwd = os.getcwd()
    os.chdir(project_dir)

    try:
        log.info("Spawning create-payload-app (PTY mode)...")
        child = spawn(" ".join(command), timeout=TIMEOUT_SECONDS, encoding="utf-8")
        child.logfile = sys.stdout

        try:
            # Step 1: Database selection
            log.info("Waiting for database selection prompt...")
            child.expect(PROMPT_DB_SELECT, timeout=45)
            log.info("Selecting PostgreSQL (sending down arrow + Enter)...")
            child.send(DOWN_ARROW)
            child.send(ENTER)

            child.expect(PROMPT_POSTGRES_SELECTED, timeout=15)
            log.info("PostgreSQL confirmed as selected.")

            # Step 2: Connection string
            log.info("Waiting for PostgreSQL connection string prompt...")
            child.expect(PROMPT_CONNECTION_STRING, timeout=15)

            log.info("Clearing default value and injecting DATABASE_URI...")
            log.debug(f"Using database_uri = {database_uri}")
            child.send(CTRL_U)
            child.sendline(database_uri)
            child.send(ENTER)

            # Stronger verification
            try:
                child.expect(
                    re.compile(r".*(?:success|connected|database|project).*", re.IGNORECASE),
                    timeout=12
                )
            except pexpect.TIMEOUT:
                log.warning(
                    "Could not find a clear success signal after sending the database URI. "
                    "Continuing anyway — the wizard may still succeed."
                )

            # Wait for completion
            log.info("Waiting for create-payload-app to finish...")
            child.expect(pexpect.EOF, timeout=TIMEOUT_SECONDS)

            rc = child.exitstatus
            if rc != 0:
                raise RuntimeError(f"create-payload-app exited with code {rc}")

            log.info("✅ Payload CMS project created successfully!")

        except pexpect.TIMEOUT:
            log.error("Timeout waiting for expected prompt.")
            _log_pexpect_context(child, "TIMEOUT")
            raise
        except pexpect.EOF:
            log.error("Unexpected EOF (process exited early).")
            _log_pexpect_context(child, "EOF")
            raise
        finally:
            if child.isalive():
                child.close(force=True)

    finally:
        os.chdir(original_cwd)


# =============================================================================
# Entry Point
# =============================================================================

def main() -> None:
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config_path = args.config
    file_config = load_config(config_path)
    merged_config = merge_config(args, file_config)

    project_dir = args.project_dir.resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    try:
        run_payload_wizard(merged_config, project_dir, dry_run=args.dry_run)
    except Exception as exc:
        log.error("Automation failed: %s", exc)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
