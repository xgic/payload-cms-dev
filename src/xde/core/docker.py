"""Docker Compose orchestration layer.

This module is one of the core abstractions in xde. It provides a clean,
high-level Python interface for controlling Docker and Docker Compose.

================================================================================
CURRENT STRATEGY & FUTURE CONSIDERATION (2026)
================================================================================

**Current Approach:**
We are deliberately using a simple subprocess-based implementation
(calling the `docker` and `docker compose` CLI commands directly).

Rationale for staying with the current approach for now:
- The Docker and Docker Compose operations we currently perform are
  relatively straightforward.
- The current implementation has low complexity and no additional
  runtime dependencies.
- It has been reliable for our needs so far.

**Future Consideration:**
We will periodically re-evaluate the Docker/Docker Compose interface.
We may rewrite this module in the future to use a more advanced or
robust API (for example: `python-on-whales`, the official Docker Python
SDK, a hybrid approach, or a small Go helper binary using Docker's
official Go Compose SDK) once our requirements grow more complex or
we encounter limitations with the current approach.

This decision will be revisited when:
- We start hitting robustness, maintainability, or feature limitations, or
- We are ready to invest in a more sophisticated backend as part of
  evolving `xde` into a high-quality importable library/framework.

The public API of this module should be kept high-level and stable
so that the underlying implementation can evolve with minimal
breaking changes for callers.

See `GROK-TASKS.md` (section on Docker/Compose Interface Strategy)
for the current long-term tracking of this item.
================================================================================

Current implementation note:
As of mid-2026 we are using a straightforward subprocess approach.
The public methods should be treated as the stable contract.

Intended capabilities:
- Full lifecycle control (up, down, build, restart, etc.)
- Good support for dry-run, streaming logs, and structured status
- Health checks and volume management
- Clean error handling and progress reporting

This abstraction is critical for both human DX and agent productivity.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from xde.core.environment import EnvironmentContext

COMPOSE_FILE = ".devcontainer/docker-compose.yml"
DEFAULT_COMPOSE_PROJECT = "xgic-payload-cms-dev-containers"
DEFAULT_CONFIG_FILE = Path(".devcontainer/create-payload-config.json")


@dataclass
class DockerComposeController:
    """Controls Docker Compose services for the dev environment."""

    env: EnvironmentContext
    compose_file: str = COMPOSE_FILE
    project_name: str = DEFAULT_COMPOSE_PROJECT

    def _run_compose(
        self,
        *args: str,
        check: bool = True,
        capture_output: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        """Run a docker compose command with consistent flags."""
        cmd = [
            "docker",
            "compose",
            "-f",
            self.compose_file,
            "-p",
            self.project_name,
            *args,
        ]
        return subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True,
        )

    def services_running(self) -> bool:
        """Return True if the main devcontainer service appears to be up.

        This is intentionally a lightweight check suitable for quick
        "are things running?" decisions (e.g. before running `xde dev`).
        """
        try:
            result = self._run_compose(
                "ps",
                "--services",
                "--filter",
                "status=running",
                capture_output=True,
            )
            # The service name in docker-compose.yml is the compose service name
            return "xgic-payload-cms-dev-containers" in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def up(
        self, *, build: bool = False, services: list[str] | None = None
    ) -> None:
        """Start services in detached mode.

        If services is provided (list of service names), only those services
        are started. This enables targeted handling (e.g. only "postgres")
        during reset so the caller's own main dev container is not recreated
        while the reset command is running inside it.
        """
        args = ["up", "-d"]
        if build:
            args.append("--build")
        if services:
            args.extend(services)
        self._run_compose(*args)

    def down(self) -> None:
        """Stop services (volumes are preserved)."""
        self._run_compose("down")

    def rm_service(
        self,
        service: str,
        *,
        force: bool = True,
        stop: bool = True,
        remove_volumes: bool = False,
    ) -> None:
        """Best-effort compose rm for a single service.

        Used by reset to stop/remove *only* the postgres container before
        attempting to remove its named data volume (so the volume rm can
        succeed). Matches the proven sequence from the legacy reset script.
        """
        args = ["rm"]
        if force:
            args.append("-f")
        if stop:
            args.append("-s")
        if remove_volumes:
            args.append("-v")
        args.append(service)
        self._run_compose(*args, check=False)

    def build(self, *, no_cache: bool = False) -> None:
        """Build images."""
        args = ["build"]
        if no_cache:
            args.append("--no-cache")
        self._run_compose(*args)

    def logs(self, follow: bool = True) -> None:
        """Follow logs (this blocks)."""
        args = ["logs"]
        if follow:
            args.append("-f")
        self._run_compose(*args, check=False)  # logs can be interrupted

    def exec(
        self, service: str, *cmd: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        """Run a command inside a service container.

        Args:
            service: Name of the compose service.
            *cmd: Command and arguments to run inside the service.
            check: If True (default), raise on non-zero exit. Set to False for
                   long-running or intentionally interruptible commands (e.g.
                   when the caller wants to handle return codes like 130/SIGINT
                   itself). This is consistent with the logs() method.
        """
        return self._run_compose("exec", service, *cmd, check=check)

    def get_payload_project_name(self) -> str:
        """Return the name of the generated Payload project folder.

        Reads from create-payload-config.json when available, with sensible
        fallback. This is useful for commands that need to operate inside
        the generated project (e.g. `dev`, certain reset behaviors).
        """
        if DEFAULT_CONFIG_FILE.exists():
            try:
                with open(DEFAULT_CONFIG_FILE, encoding="utf-8") as f:
                    data: dict[str, Any] = json.load(f)
                if name := data.get("projectName"):
                    return str(name)
            except (json.JSONDecodeError, OSError):
                pass
        return "my-payload-cms"

    def get_db_config(self) -> tuple[str, str]:
        """Return (db_name, db_user) from create-payload-config.json.

        Prefers dbName/dbUser. Falls back to dbUri parse or defaults.
        Mirrors legacy _get_db_details_from_config for fidelity.
        """
        default_db = "payload_db"
        default_user = "payload"
        if not DEFAULT_CONFIG_FILE.exists():
            return default_db, default_user
        try:
            with DEFAULT_CONFIG_FILE.open(encoding="utf-8") as f:
                cfg: dict[str, Any] = json.load(f)
            db_name = cfg.get("dbName") or default_db
            db_user = cfg.get("dbUser") or default_user
            # Fallback parse from dbUri (robustness)
            db_uri = cfg.get("dbUri") or ""
            if db_uri and (db_name == default_db or db_user == default_user):
                try:
                    if "://" in db_uri:
                        after = db_uri.split("://", 1)[1]
                        if "@" in after and db_user == default_user:
                            creds = after.split("@", 1)[0]
                            if ":" in creds:
                                db_user = creds.split(":", 1)[0] or db_user
                        if "/" in after and db_name == default_db:
                            after_host = after.split("@", 1)[-1]
                            path = after_host.split("/", 1)[-1].split("?")[0]
                            if path:
                                db_name = path or db_name
                except Exception:
                    pass
            return db_name, db_user
        except Exception:
            return default_db, default_user

    def db_ready(self) -> bool:
        """Check if PostgreSQL is accepting connections using pg_isready.

        Uses real db user from config (not hardcoded).
        """
        _, db_user = self.get_db_config()
        try:
            result = self._run_compose(
                "exec",
                "-T",
                "postgres",
                "pg_isready",
                "-U",
                db_user,
                capture_output=True,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def remove_volume(self, volume_name: str) -> bool:
        """Attempt to remove a Docker volume.

        Uses the top-level `docker volume rm` command (docker compose has no
        'volume' subcommand; that was the source of the noisy "unknown docker
        command" + full help spam in reset).

        Returns True if removal succeeded or the volume did not exist.
        Output is captured so expected "not found" cases stay quiet.
        """
        try:
            result = subprocess.run(
                ["docker", "volume", "rm", "-f", volume_name],
                check=False,
                capture_output=True,
                text=True,
            )
            # With -f, modern docker returns 0 whether the volume was removed
            # or simply did not exist. Non-zero is a real failure (e.g. in use
            # without -f, permission issues). We treat rc==0 as success.
            return result.returncode == 0
        except Exception:
            return False
