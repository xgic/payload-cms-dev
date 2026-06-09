"""Payload project setup / ensure logic (modular and testable).

This module extracts the project creation behavior that was previously
only in .devcontainer/scripts/setup-payload.sh. It is now:

- Callable from `xde setup payloadcms` (the new nested subcommand).
- Callable as the final step of `xde reset` (so "Next: xde dev" works
  immediately after reset without needing a container restart or hook).
- Idempotent and quiet on the happy path (no output when the project
  already looks complete). This keeps devcontainer startup clean.

Design:
- Small pure functions for testability (load, is_complete, build args).
- One ensure function that performs the side-effecting work.
- Lives in core/ so it can be imported by commands and reset without
  pulling in CLI concerns.
- Follows the same "direct subprocess inside container" model as dev:
  we run pnpx / pnpm directly when inside (the normal case).

See AGENTS.md (Grok workflows, pitfalls) and docs/grok-playbooks.md for
context on why creation is now a first-class, reusable xde operation.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from xde.core.docker import DEFAULT_CONFIG_FILE
from xde.utils.output import print_info, print_success, print_warning


def load_create_payload_config(
    config_path: Path = DEFAULT_CONFIG_FILE,
) -> dict[str, Any]:
    """Load create-payload-config.json (or sensible defaults).

    Pure function. Matches the fields used by the legacy setup script.
    """
    defaults: dict[str, Any] = {
        "projectName": "my-payload-cms",
        "template": "website",
        "dbAdapter": "postgres",
        "agent": "none",
        "dbUri": "",
    }
    if not config_path.exists():
        return defaults
    try:
        with config_path.open(encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
        # Overlay provided keys onto defaults (so partial configs work)
        for k, v in data.items():
            if v is not None:
                defaults[k] = v
        return defaults
    except (json.JSONDecodeError, OSError):
        return defaults


def get_project_name(config: dict[str, Any]) -> str:
    """Extract projectName with safe default."""
    name = config.get("projectName")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return "my-payload-cms"


def is_payload_project_complete(project_dir: Path) -> bool:
    """Return True if project_dir looks like a finished Payload app.

    Checks for payload.config.{ts,js} at root or under src/ (covers the
    standard template and minor layout variants). Pure and fast.
    """
    if not project_dir.is_dir():
        return False
    candidates = [
        project_dir / "payload.config.ts",
        project_dir / "payload.config.js",
        project_dir / "src" / "payload.config.ts",
        project_dir / "src" / "payload.config.js",
    ]
    return any(p.exists() for p in candidates)


def build_create_payload_command(
    project_name: str,
    *,
    template: str = "website",
    db_adapter: str = "postgres",
    db_connection_string: str | None = None,
    agent: str = "none",
) -> list[str]:
    """Return the argv list for a non-interactive create-payload-app run.

    Mirrors the exact flags used by the legacy setup script (select-db
    and select-agent handling in create-payload-app).
    """
    cmd = [
        "pnpx",
        "create-payload-app@latest",
        project_name,
        "-t",
        template,
        "--use-pnpm",
    ]

    if db_connection_string:
        cmd.extend(
            ["--db", db_adapter, "--db-connection-string", db_connection_string]
        )
    else:
        cmd.extend(["--db", db_adapter, "--db-accept-recommended"])

    if agent and str(agent).lower() not in ("", "none"):
        cmd.extend(["--agent", str(agent)])
    else:
        cmd.append("--no-agent")

    return cmd


def _sync_live_env_into_project(
    project_dir: Path, live_db_uri: str, live_payload_secret: str
) -> None:
    """Best-effort sync of live credentials into the generated project's .env.

    The container-level .env uses DATABASE_URI; generated projects use
    DATABASE_URL (plus PAYLOAD_SECRET). We rewrite only if values exist.
    Uses pure Python so it is portable (no GNU/BSD sed -i differences).
    """
    gen_env = project_dir / ".env"
    if not gen_env.is_file():
        return

    try:
        content = gen_env.read_text(encoding="utf-8")
        changed = False

        if live_db_uri:
            # Replace DATABASE_URL=... line (website template convention)
            new_content = re.sub(
                r"^DATABASE_URL=.*$",
                f"DATABASE_URL={live_db_uri}",
                content,
                flags=re.MULTILINE,
            )
            if new_content != content:
                content = new_content
                changed = True

        if live_payload_secret:
            new_content = re.sub(
                r"^PAYLOAD_SECRET=.*$",
                f"PAYLOAD_SECRET={live_payload_secret}",
                content,
                flags=re.MULTILINE,
            )
            if new_content != content:
                content = new_content
                changed = True

        if changed:
            gen_env.write_text(content, encoding="utf-8")
    except Exception:
        # Never let sync failure break creation flow
        pass


def ensure_payload_project(*, quiet: bool = False) -> int:
    """Ensure the Payload CMS project directory exists and is usable.

    Idempotent:
    - If a complete project already exists: return 0 with zero output.
    - If directory exists but looks incomplete: warn, then attempt create.
    - Otherwise: run the non-interactive create-payload-app flow.

    Approves @swc/core build scripts early (suppresses noisy pnpm warning).
    After successful create, syncs live DATABASE_URI / PAYLOAD_SECRET from
    the container environment into the project's .env.

    Returns 0 on success / best-effort completion (creation warnings are
    non-fatal to match prior hook behavior and keep devcontainer startup
    robust). Non-zero only for truly unrecoverable early failures.
    """
    cfg = load_create_payload_config()
    project_name = get_project_name(cfg)
    project_dir = Path(project_name)

    if is_payload_project_complete(project_dir):
        # Silent success is intentional for the postStart hook path and
        # for clean "already ready" cases in reset/dev flows.
        return 0

    if project_dir.exists() and not quiet:
        print_warning(
            f"Directory '{project_name}' exists but does not appear to be "
            "a complete Payload project. Creation may overwrite or fail."
        )

    template = str(cfg.get("template") or "website")
    db_adapter = str(cfg.get("dbAdapter") or "postgres")
    json_db_uri = str(cfg.get("dbUri") or "")
    agent = str(cfg.get("agent") or "none")

    live_db_uri = os.environ.get("DATABASE_URI", "")
    live_secret = os.environ.get("PAYLOAD_SECRET", "")

    db_uri_for_cli: str | None = live_db_uri or json_db_uri or None

    # Suppress pnpm "Ignored build scripts" for @swc/core before the
    # create step triggers its internal pnpm install.
    try:
        subprocess.run(
            ["corepack", "pnpm", "approve-builds", "@swc/core"],
            check=False,
            capture_output=True,
        )
    except Exception:
        pass

    cmd = build_create_payload_command(
        project_name,
        template=template,
        db_adapter=db_adapter,
        db_connection_string=db_uri_for_cli,
        agent=agent,
    )

    if not quiet:
        print_info(
            f"Starting Payload CMS project creation for '{project_name}' "
            f"(template: {template}, db: {db_adapter})..."
        )

    try:
        result = subprocess.run(cmd, check=False)
    except FileNotFoundError as e:
        print_warning(f"Required tool not found for project creation: {e}")
        return 1

    if result.returncode == 0:
        if not quiet:
            print_success("Payload project created successfully.")

        # Post-create credential sync (defensive; create-payload-app may
        # rewrite .env during its own manage-env-files step).
        if project_dir.is_dir():
            _sync_live_env_into_project(project_dir, live_db_uri, live_secret)

        return 0

    # Best-effort: do not hard-fail the caller (hook or reset). The
    # prior shell script explicitly continued after create warnings.
    if not quiet:
        print_warning(
            f"create-payload-app exited with status {result.returncode}."
        )
        print_info(
            "This is often harmless. Check the project directory. "
            "You can re-run with: xde setup payloadcms"
        )
    return 0
