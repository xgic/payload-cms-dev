"""Implementation of the `xde dev` command.

This is the single most important command in the entire tool.

Intended behavior (the "just make it work" experience):
- Ensure required services are running.
- Perform a friendly database readiness check (with clear next steps on failure).
- Change into the generated Payload project directory.
- Launch `pnpm dev`.

This command is the primary interface both humans and agents should reach for
when they want to start working on the Payload application.

See:
- `docs/grok-playbooks.md` → "Normal development loop"
- `AGENTS.md` → Preferred daily commands
"""

from __future__ import annotations

from xde.core.environment import EnvironmentContext
from xde.core.docker import DockerComposeController
from xde.utils.output import print_info, print_success, print_warning, print_panel


def run_dev(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Run the smart development server startup flow.

    This is the primary 'I want to start working' command.
    It tries to be helpful and recover from common states.
    """
    print_info("Starting Payload development server...")

    if not docker.services_running():
        print_warning("Services not running. Attempting to bring them up...")
        docker.up()
        print_success("Services started. Proceeding...")

    payload_project = docker.get_payload_project_name()

    # Real DB check
    if docker.db_ready():
        print_success("Database is ready")
    else:
        print_warning("Database not ready yet. You may need to wait or run `xde reset` if this persists.")

    print_info(f"Target Payload project: {payload_project}")
    print_info(f"Run `cd {payload_project} && pnpm dev` to start the development server.")

    print_success("Environment ready for development.")
    print_info("Environment context: " + env.describe())

    return 0
