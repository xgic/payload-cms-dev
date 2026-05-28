"""Environment inspection and management commands."""

from __future__ import annotations

from pathlib import Path

from xde.core.environment import EnvironmentContext
from xde.core.docker import DockerComposeController
from xde.utils.output import print_info, print_success


ENV_FILE = Path(".devcontainer/.env")


def run_env(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Show current environment status (lightweight inspection command)."""
    print_info("Development environment status:")

    if ENV_FILE.exists():
        print_success(f".env file exists at {ENV_FILE}")
        # In a more complete version we would show non-secret keys or status
    else:
        print_info(".env file not found (run init-env or xde up to generate)")

    services_ok = docker.services_running()
    if services_ok:
        print_success("Compose services: appear to be running")
    else:
        print_info("Compose services: not detected as running")

    payload_project = docker.get_payload_project_name()
    print_info(f"Configured Payload project: {payload_project}")

    print_info("Environment context: " + env.describe())

    return 0