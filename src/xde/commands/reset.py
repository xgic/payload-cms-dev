"""Reset command (fast targeted reset)."""

from __future__ import annotations

from xde.core.environment import EnvironmentContext
from xde.core.docker import DockerComposeController
from xde.utils.output import print_success


def run_reset(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    print_success(
        "Would perform fast reset (project folder + Postgres volume) - "
        "not yet implemented"
    )
    return 0
