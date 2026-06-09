"""Diagnostic commands (check, etc.)."""

from __future__ import annotations

import json

from xde.core.docker import DockerComposeController
from xde.core.environment import EnvironmentContext
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
    db_ok = docker.db_ready()
    payload_project = docker.get_payload_project_name()

    use_json = getattr(args, "json", False)

    if use_json:
        result = {
            "services_running": services_ok,
            "database_ready": db_ok,
            "payload_project": payload_project,
            "environment": env.describe(),
            "overall_ok": services_ok and db_ok,
        }
        print(json.dumps(result, indent=2))
        return 0 if (services_ok and db_ok) else 1
    else:
        if services_ok:
            print_success("Docker Compose services: running")
        else:
            print_warning(
                "Docker Compose services: not all services appear to be running"
            )
            print_info("Suggestion: Run `xde up` to start services.")

        if db_ok:
            print_success("Database connectivity: ready (pg_isready)")
        else:
            print_warning("Database connectivity: not ready")
            print_info(
                "Suggestion: The database may still be starting or needs reset."
            )

        print_info(f"Expected Payload project folder: {payload_project}")

        if services_ok and db_ok:
            print_success("Basic environment check passed")
            return 0
        else:
            return 1
