"""Implementation of the `xde dev` command.

This is the smart replacement for the old `make dev` target.
Performs DB readiness check and gives friendly guidance instead of raw errors.
"""

from __future__ import annotations

from xde.core.environment import EnvironmentContext
from xde.core.docker import DockerComposeController
from xde.utils.output import print_info, print_warning, print_panel


def run_dev(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Run the smart development server startup flow."""
    print_info("Starting Payload development server...")

    if not docker.services_running():
        print_warning("Development containers are not running.")
        print_panel(
            "Next step",
            "Run [bold]xde up[/bold] first, then [bold]xde dev[/bold] again.",
            style="yellow",
        )
        return 1

    # TODO: real DB check (pg_isready or similar via docker exec)
    # TODO: cd to project dir (from create-payload-config.json)
    #       and exec pnpm dev

    print_info("DB check would happen here (not yet implemented).")
    print_info("Would now run: pnpm dev inside the project directory.")
    print_info("Environment detected: " + env.describe())

    return 0
