"""Setup subcommand family (nested under `xde setup`).

Currently provides `xde setup payloadcms` which ensures the generated
Payload CMS application directory is present and ready.

This structure was chosen so that future setup targets (e.g. additional
components, staging mirrors, or sample data) can be added as siblings
without bloating the top-level command surface or requiring changes to
`xde --help`.

The implementation delegates to the testable core in
`xde.core.project.ensure_payload_project`.
"""

from __future__ import annotations

from xde.core.docker import DockerComposeController
from xde.core.environment import EnvironmentContext
from xde.core.project import ensure_payload_project


def run_setup_payloadcms(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Run the payloadcms setup / ensure step.

    Idempotent and safe to call from:
    - The devcontainer postStartCommand (via the thin shim script).
    - `xde reset` as its final action (makes the post-reset guidance work).
    - Direct invocation by a human or agent: `xde setup payloadcms`.
    """
    # We receive env and docker for consistency with other commands and
    # future use (e.g. name lookup via controller), but the ensure logic
    # loads its own config and prefers live env vars for secrets.
    return ensure_payload_project()
