"""Docker Compose orchestration layer.

This module is one of the core abstractions in xde. It provides a clean,
high-level Python interface for controlling Docker and Docker Compose.

================================================================================
DESIGN DECISION (2026)
================================================================================

**Short-to-Medium Term (v1 and initial production use):**
We are moving toward a hybrid approach:
- Use the official Docker Python SDK (`docker` package) for low-level
  Docker Engine operations (containers, exec, volumes, image management,
  health checks, etc.).
- Use `python-on-whales` (a mature, actively maintained wrapper around
  the official Docker CLI) for Compose operations, OR continue with a
  well-abstracted subprocess layer if we want to stay extremely light on
  dependencies.

The public API of this module must remain high-level and stable so that
it can later be backed by different implementations.

**Long Term (when xde becomes a serious importable library/framework):**
We should seriously evaluate a "controlled Go helper" pattern:
- A small, well-maintained Go binary that uses Docker's official Go
  Compose SDK (`github.com/docker/compose/v5/pkg/api`).
- The Go binary is shipped alongside the Python package (or installed
  on-demand) and is called via a clean, stable interface (JSON over
  stdio, local gRPC, or Unix socket).
- This gives us native, robust Compose semantics without the limitations
  of the Python ecosystem.

This pattern is successfully used by several mature projects (HashiCorp
tools, Temporal, various CNCF components) when they need capabilities
that are only first-class in Go.

**Why not pure official SDK today?**
The official `docker` Python SDK has excellent Engine support but weak/
incomplete support for full `docker compose` project semantics.

**Guiding Principle:**
The interface exposed by `DockerComposeController` (and any future
`DockerEngineClient`) must be designed for library consumers first,
CLI second. Implementation details should be hidden.

See `docs/architecture.md` and `GROK-TASKS.md` for related long-term goals.
================================================================================

Current implementation note:
As of mid-2026 we are still using subprocess for Compose while the
hybrid strategy is being evaluated. The public methods should be
treated as the stable contract.

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

    def up(self, *, build: bool = False) -> None:
        """Start all services in detached mode."""
        args = ["up", "-d"]
        if build:
            args.append("--build")
        self._run_compose(*args)

    def down(self) -> None:
        """Stop services (volumes are preserved)."""
        self._run_compose("down")

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

    def exec(self, service: str, *cmd: str) -> subprocess.CompletedProcess[str]:
        """Run a command inside a service container."""
        return self._run_compose("exec", service, *cmd)

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

    def db_ready(self) -> bool:
        """Check if PostgreSQL is accepting connections using pg_isready.

        Runs pg_isready inside the postgres container for accuracy.
        Returns True only if the database responds as ready.
        """
        try:
            result = self._run_compose(
                "exec",
                "-T",
                "postgres",
                "pg_isready",
                "-U",
                "payload",  # default user from config examples
                capture_output=True,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def remove_volume(self, volume_name: str) -> bool:
        """Attempt to remove a Docker volume.

        Returns True if removal succeeded or volume did not exist.
        """
        try:
            self._run_compose("volume", "rm", "-f", volume_name)
            return True
        except Exception:
            return False
