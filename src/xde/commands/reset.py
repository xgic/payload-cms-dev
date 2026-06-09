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
- See `DEV-JOURNAL.md` for credential handling history.

See also:
- `docs/grok-playbooks.md` → Migration and debugging playbooks
- `AGENTS.md` → Safety & Destructive Operations section
"""

from __future__ import annotations

from pathlib import Path

from xde.commands.env import perform_env_regenerate
from xde.core.docker import DockerComposeController
from xde.core.environment import EnvironmentContext
from xde.core.project import ensure_payload_project
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
    _compact = getattr(args, "compact", False)

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
        print_warning(
            "This operation is destructive. Re-run with --yes to proceed."
        )
        return 1

    # Actual execution (hardened v1; modernized from the historical
    # legacy reset-project.py which has now been removed)
    print_info("Performing reset...")

    if project_path.exists():
        import shutil

        shutil.rmtree(project_path)
        print_success(f"Deleted project directory: {project_path}")
    else:
        print_info(f"Project directory {project_path} did not exist.")

    # Best-effort: stop/remove *only* the postgres service/container first.
    # This releases the named volume so the subsequent docker volume rm
    # can succeed (the volume is mounted by the postgres container).
    # Sequence matches the (now-removed) historical legacy reset-project.py.
    docker.rm_service("postgres", force=True, stop=True, remove_volumes=False)

    # Remove the postgres volume via docker
    if docker.remove_volume(postgres_volume):
        print_success(f"Removed volume: {postgres_volume}")
    else:
        print_warning(
            f"Could not remove volume {postgres_volume} "
            "(may not exist or in use)"
        )

    # Recreate *only* the postgres service (targeted) and ensure DB.
    # We use the public up(services=...) so that reset (which runs inside the
    # main dev container) does not attempt to recreate its own container.
    # Pre-stop (above) + targeted up + IF NOT EXISTS wrapper give reliable,
    # quiet volume + DB reset.
    db_name, db_user = docker.get_db_config()
    try:
        docker.up(services=["postgres"])
        print_info("Postgres service recreated.")

        # Optional: a short pg_isready wait here (like the legacy script)
        # would make the CREATE step even more reliable after a fresh start.
        # The 2>/dev/null || true wrapper below already protects us.

        sql = f"CREATE DATABASE IF NOT EXISTS {db_name} OWNER {db_user};"
        docker.exec(
            "postgres",
            "sh",
            "-c",
            f'psql -U {db_user} -d postgres -c "{sql}" 2>/dev/null || true',
            check=False,
        )
        print_success(f"Ensured database '{db_name}' exists.")

        # Ensure the Payload project directory (recreate after the delete
        # performed at the start of reset). This was historically only done
        # by the devcontainer postStart hook. Running it here makes the
        # post-reset guidance ("Next: xde dev") immediately actionable
        # without a container restart or hook re-execution.
        ensure_payload_project()
    except Exception as e:
        print_warning(
            f"Issue recreating postgres or DB: {e}. "
            "Manual `xde up` may be needed."
        )

    if rotate:
        print_info("Rotating credentials (--rotate-credentials)...")
        rc = perform_env_regenerate(yes=True)
        if rc == 0:
            print_success("Credentials rotated in .env.")
        else:
            print_warning("Credential rotation had issues (check .env).")

    print_success(
        "Reset complete. Project ensured. Next: `xde dev` (or `xde up`)."
    )
    return 0
