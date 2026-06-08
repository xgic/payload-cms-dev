"""Implementation of the `xde dev` command.

This is the single most important command in the entire tool.

Intended behavior (the "just make it work" experience):
- Ensure required services are running.
- Perform a friendly DB readiness check (with clear next steps on failure).
- Change into the generated Payload project directory.
- Launch the project's dev server (`pnpm dev` by default for this template).

Execution model (architectural rule):
- When running **inside** the main dev container (the default and most common
  case), `xde dev` runs the dev command directly as a normal subprocess.
  This gives native, clean signal handling (Ctrl+C etc.) with no unnecessary
  Docker indirection for the application's own dev server.
- `xde` only uses Docker or Docker Compose commands when it is legitimately
  required for controlling *other* containers/services from within the main
  dev container (e.g. the DB readiness check against the postgres service),
  or when executing commands for automated CI/CD/Testing from *outside* the
  main dev container (host-side orchestration).

This command is the primary interface both humans and agents should reach for
when they want to start working on the Payload application.

See:
- `docs/grok-playbooks.md` → "Normal development loop"
- `AGENTS.md` → Preferred daily commands
"""

from __future__ import annotations

import subprocess

from xde.core.docker import DockerComposeController
from xde.core.environment import EnvironmentContext, EnvironmentType
from xde.utils.output import (
    print_info,
    print_success,
    print_warning,
)


def run_dev(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Run the smart development server startup flow.

    This is the primary 'I want to start working' command.
    It tries to be helpful and recover from common states.

    When running inside the dev container (the normal case), the actual
    dev server (`pnpm dev`) is executed directly for clean signal handling.
    Docker is only used for legitimate cross-service operations (e.g. DB
    checks) or when `xde dev` is invoked from outside the container.
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
        print_warning("Database not ready yet. You may need `xde reset`.")

    print_info(f"Target Payload project: {payload_project}")

    # Decide how to launch the dev server.
    #
    # Architectural rule (per project design):
    # - xde only uses Docker/Docker Compose when it is required for
    #   controlling *other* containers/services from within the main dev
    #   container, or when running commands for CI/CD/Testing from *outside*
    #   the main dev container (host side).
    # - For the common case of running the application's own dev server
    #   **inside** the dev container, we run the command directly as a normal
    #   subprocess. This gives native, clean signal handling (Ctrl+C etc.)
    #   and avoids an unnecessary docker compose exec indirection layer.
    #
    # Pre-flight checks (services_running, db_ready) may still legitimately
    # use the controller because they talk to other services (e.g. postgres).

    if env.env_type == EnvironmentType.DEV_CONTAINER:
        # Default / common case: we are already inside the main dev container.
        # Run pnpm dev directly (native signal handling, clean Ctrl+C behavior).
        try:
            print_info(f"Launching pnpm dev inside {payload_project}...")
            # Note: pnpm dev is long-running; attaches until interrupted.
            # We use check=False to distinguish clean user interrupt
            # (returncode 130 / SIGINT) from real launch failure.
            project_dir = f"/workspace/{payload_project}"
            result = subprocess.run(
                ["pnpm", "dev"],
                cwd=project_dir,
                check=False,
            )

            # Handle user-initiated stop (Ctrl+C / SIGINT) cleanly.
            # 130 == 128 + SIGINT is the conventional shell exit code.
            if result.returncode in (130, -2, 2):
                print_info("Development server stopped by user (Ctrl+C).")
                return 0

            if result.returncode != 0:
                # Real failure (not a user interrupt).
                print_warning(f"pnpm dev exited with code {result.returncode}.")
                print_info(
                    f"Fallback: cd {payload_project} && pnpm dev "
                    "(or xde shell)."
                )
                return result.returncode or 1

            # Normal clean exit of the dev server (rare for long-running dev).
            print_info("Development server exited cleanly.")
            return 0

        except KeyboardInterrupt:
            # This can happen depending on how the signal is delivered to the
            # Python process while the child is running.
            print_info("Development server stopped by user (Ctrl+C).")
            return 0

    else:
        # Outside the main dev container (host, CI, or other environments):
        # Use the controller to run the command inside the target container.
        # This is the "executing from outside" case.
        try:
            print_info(
                f"Launching pnpm dev inside {payload_project} "
                "(via container)..."
            )
            # Note: pnpm dev is long-running; attaches until interrupted.
            docker.exec(
                "xgic-payload-cms-dev-containers",
                "sh",
                "-c",
                f"cd /workspace/{payload_project} && pnpm dev",
                check=False,  # caller handles non-zero / interrupts
            )
        except Exception as e:
            print_warning(f"Failed to launch pnpm dev: {e}")
            print_info(
                f"Fallback: cd {payload_project} && pnpm dev (or xde shell)."
            )

    print_success("Environment ready for development.")
    print_info("Environment context: " + env.describe())

    return 0
