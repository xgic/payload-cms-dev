"""Docker Compose orchestration layer.

This module provides the single point of contact for all Docker Compose
operations in the project.

Design principles:
- Uses only stdlib `subprocess` (no heavy dependencies like python-on-whales).
- Designed to be easily testable and mockable.
- Central place for compose project name, file paths, and command construction.

Current capabilities (being actively expanded):
- Start/stop/build services
- Basic service status checks
- Command execution inside containers

Intended future improvements:
- Better structured output from `docker compose ps`
- Streaming log support
- Health check helpers

This is a critical abstraction for agent productivity — it allows Grok
to reason about container state without writing raw shell commands.

See also:
- `AGENTS.md` → Preferred commands section
- `docs/grok-playbooks.md` → "Debug a broken environment" playbook
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
