"""Lifecycle commands: up, down, etc."""

from __future__ import annotations

from pathlib import Path

from xde.core.environment import EnvironmentContext
from xde.core.docker import DockerComposeController
from xde.utils.output import print_success, print_info, print_warning


def run_up(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    print_info("Starting services...")
    docker.up()
    print_success("Services are up (detached)")
    return 0


def run_down(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    print_info("Stopping services...")
    docker.down()
    print_success("Services stopped (volumes preserved)")
    return 0


def run_build(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    no_cache = getattr(args, "no_cache", False)
    print_info("Building services" + (" (no cache)" if no_cache else "") + "...")
    docker.build(no_cache=no_cache)
    print_success("Build complete")
    return 0


def run_logs(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Follow logs for all services (blocks until interrupted)."""
    print_info("Following logs (press Ctrl+C to exit)...")
    docker.logs(follow=True)
    return 0


def run_shell(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Open an interactive shell in the primary service."""
    print_info("Opening shell in primary service (type 'exit' to leave)...")
    # Use 'node' as the main service user, matching the devcontainer setup
    try:
        docker.exec("xgic-payload-cms-dev-containers", "bash")
    except Exception:
        # Fallback if exec fails in this context
        print_info("Shell session ended or failed to attach.")
    return 0


def run_clean(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Full environment cleanup (volumes + .env). Extremely destructive."""
    yes = getattr(args, "yes", False)

    print_warning("This will delete Docker volumes AND the generated .env file.")
    print_warning("This is more destructive than `xde reset`.")

    if not yes:
        print_warning("Re-run with --yes only if you are absolutely sure.")
        return 1

    print_info("Performing full cleanup...")

    # Stop services first
    try:
        docker.down()
    except Exception:
        pass

    # Remove volumes (best effort)
    try:
        docker._run_compose("down", "-v")  # type: ignore[attr-defined]
    except Exception:
        pass

    # Remove .env
    env_file = Path(".devcontainer/.env")
    if env_file.exists():
        env_file.unlink()
        print_success("Removed .env file")

    print_success("Full cleanup complete. You will need to re-initialize the environment.")
    return 0
