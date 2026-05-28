"""Diagnostic commands (check, etc.)."""

from __future__ import annotations

from xde.core.environment import EnvironmentContext
from xde.core.docker import DockerComposeController
from xde.utils.output import print_info, print_success, print_warning


def run_check(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Basic health check for the development environment.

    This is intentionally lightweight but useful for both humans and agents
    to quickly determine if the environment is in a usable state.
    """
    print_info("Running environment health checks...")

    services_ok = docker.services_running()
    if services_ok:
        print_success("Docker Compose services: running")
    else:
        print_warning("Docker Compose services: not all services appear to be running")
        print_info("Suggestion: Run `xde up` to start services.")

    # Placeholder for future real DB check (pg_isready via docker exec)
    print_info("Database connectivity: check not yet implemented (will use pg_isready)")

    payload_project = docker.get_payload_project_name()
    print_info(f"Expected Payload project folder: {payload_project}")

    if services_ok:
        print_success("Basic environment check passed (services up)")
        return 0
    else:
        return 1
