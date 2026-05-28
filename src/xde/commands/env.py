"""Environment inspection and management commands."""

from __future__ import annotations
import json
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
            print_info(".env file not found (run init-env or xde up to generate)")

        if services_ok:
            print_success("Compose services: appear to be running")
        else:
            print_info("Compose services: not detected as running")

        print_info(f"Configured Payload project: {payload_project}")
        print_info("Environment context: " + env.describe())

        return 0