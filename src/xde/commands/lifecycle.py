"""Lifecycle commands: up, down, etc."""

from __future__ import annotations

from xde.core.environment import EnvironmentContext
from xde.core.docker import DockerComposeController
from xde.utils.output import print_success, print_info


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
