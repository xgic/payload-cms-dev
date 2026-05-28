"""Diagnostic commands (check, etc.)."""

from __future__ import annotations

from xde.core.environment import EnvironmentContext
from xde.core.docker import DockerComposeController
from xde.utils.output import print_success


def run_check(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    print_success("DB/service check would run here (not yet implemented)")
    return 0
