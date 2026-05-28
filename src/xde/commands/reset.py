"""Reset command (fast targeted reset).

This is one of the highest-value and highest-risk commands in the project.

What it does (by design):
- Deletes the generated Payload project folder.
- Resets only the Postgres data volume.
- **Deliberately leaves credentials in `.env` alone** (this avoids the classic
  stale credentials between a running container and the `.env` file on disk).

This command exists because full `make clean` / `make rebuild` cycles are
too heavy for daily development. It provides a fast, safe "nuclear option"
for the most common form of environment corruption.

Critical agent guidance:
- Always use `--dry-run` first.
- Be extremely conservative with `--rotate-credentials`.
- See `DEV-JOURNAL.md` for important historical context around credential handling.

See also:
- `docs/grok-playbooks.md` → Migration and debugging playbooks
- `AGENTS.md` → Safety & Destructive Operations section
"""

from __future__ import annotations

from pathlib import Path

from xde.core.environment import EnvironmentContext
from xde.core.docker import DockerComposeController
from xde.utils.output import print_info, print_success, print_warning


def run_reset(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Fast targeted reset (project folder + Postgres volume).

    This is the recommended safe reset for daily development.
    It deliberately does NOT touch the .env file by default.
    """
    dry_run = getattr(args, "dry_run", False)
    yes = getattr(args, "yes", False)
    rotate = getattr(args, "rotate_credentials", False)

    payload_project = docker.get_payload_project_name()
    project_path = Path(payload_project)
    postgres_volume = f"{docker.project_name}-postgres-data"

    print_info("Planned actions for reset:")
    print_info(f"  - Delete directory: {project_path}")
    print_info(f"  - Remove Docker volume: {postgres_volume}")
    if rotate:
        print_warning("  - ALSO rotate database credentials (DANGEROUS)")

    if dry_run:
        print_success("Dry run complete. No changes were made.")
        return 0

    if not yes:
        print_warning("This operation is destructive. Re-run with --yes to proceed.")
        return 1

    # Actual execution (basic version for v1)
    print_info("Performing reset...")

    if project_path.exists():
        import shutil
        shutil.rmtree(project_path)
        print_success(f"Deleted project directory: {project_path}")
    else:
        print_info(f"Project directory {project_path} did not exist.")

    # Remove the postgres volume via docker
    if docker.remove_volume(postgres_volume):
        print_success(f"Removed volume: {postgres_volume}")
    else:
        print_warning(f"Could not remove volume {postgres_volume} (may not exist or in use)")

    if rotate:
        print_warning("Credential rotation requested but not yet implemented in this build.")

    print_success("Reset complete. You will likely want to run `xde up` or `xde dev` next.")
    return 0
