"""Schema generation command.

This makes `xde schema` the primary way to (re)generate the
create-payload-config JSON schema used for IntelliSense and validation.
It delegates to the existing generator script (keeps it as source of truth
during transition; later can internalize the Pydantic model).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from xde.core.docker import DockerComposeController
from xde.core.environment import EnvironmentContext
from xde.utils.output import print_info, print_success, print_warning


def run_schema(
    args: object,
    *,
    env: EnvironmentContext,
    docker: DockerComposeController,
) -> int:
    """Generate (or refresh) the config schema + docs."""
    script = Path(".devcontainer/config/generate_schema.py")
    if not script.exists():
        print_warning(f"Generator not found: {script}")
        return 1

    print_info("Generating create-payload-config JSON schema...")
    try:
        subprocess.check_call([sys.executable, str(script)])
        print_success(
            "Schema written. IntelliSense updated for "
            "create-payload-config.json"
        )
        return 0
    except subprocess.CalledProcessError as e:
        print_warning(f"Generator exited with code {e.returncode}")
        return e.returncode or 1
    except Exception as e:
        print_warning(f"Failed to run generator: {e}")
        return 1
