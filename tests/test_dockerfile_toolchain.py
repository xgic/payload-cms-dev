"""Toolchain pins encoded in the producer Dockerfile and Compose exemplar."""

from __future__ import annotations

import os
import pwd
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = REPO_ROOT / ".devcontainer" / "Dockerfile"
COMPOSE = REPO_ROOT / ".devcontainer" / "docker-compose.yml"
ENTRYPOINT = (
    REPO_ROOT / ".devcontainer" / "scripts" / "xgic-devcontainer-entrypoint"
)


def _bash_available() -> bool:
    bash = shutil.which("bash")
    if not bash:
        return False
    probe = subprocess.run(
        [bash, "-c", "echo ok"],
        check=False,
        capture_output=True,
        text=True,
    )
    return probe.returncode == 0 and "ok" in probe.stdout


def test_payload_cms_cli_pypi_pin() -> None:
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pin = "xgic-payload-cms-cli>=0.2.5,<0.3"
    assert pin in dockerfile
    assert pin in pyproject


def test_pnpm_is_pinned_via_corepack_prepare() -> None:
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert "corepack prepare pnpm@10.34.5 --activate" in text
    assert "corepack use pnpm@10" not in text
    assert "COREPACK_DEFAULT_TO_LATEST=0" in text
    assert "COREPACK_ENABLE_AUTO_PIN=0" in text
    assert "COREPACK_HOME=/usr/local/share/corepack" in text


def test_next_telemetry_disabled() -> None:
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert "NEXT_TELEMETRY_DISABLED=1" in text
    assert "PGDATABASE=payload_db" not in text


def test_dockerfile_installs_libpq_profile_writer() -> None:
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert "write_libpq_profile.py" in text


def test_git_dx_installed_outside_workspace() -> None:
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert "/usr/local/lib/xgic/git-dx/" in text
    assert (
        'ENTRYPOINT ["/usr/local/bin/xgic-devcontainer-entrypoint"]' in text
    )
    assert "USER ${APP_USER}" in text
    # Bind-mount overlay must not be the Git DX runtime path.
    assert "COPY .devcontainer/scripts/configure-git-dx.sh" in text
    assert "COPY .devcontainer/scripts/xgic-devcontainer-entrypoint" in text


def test_producer_compose_does_not_run_workspace_git_dx() -> None:
    text = COMPOSE.read_text(encoding="utf-8")
    assert "/workspace/.devcontainer/scripts" not in text
    assert 'user: "0:0"' in text
    assert "runuser" in text


@pytest.mark.skipif(not _bash_available(), reason="bash required")
def test_entrypoint_shell_syntax() -> None:
    result = subprocess.run(
        ["bash", "-n", str(ENTRYPOINT)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr + result.stdout


@pytest.mark.skipif(not _bash_available(), reason="bash required")
def test_entrypoint_execs_command_when_git_dx_missing(
    tmp_path: Path,
) -> None:
    env = os.environ.copy()
    env["XGIC_GIT_DX_HOME"] = str(tmp_path / "missing-git-dx")
    env["APP_USER"] = pwd.getpwuid(os.getuid()).pw_name
    result = subprocess.run(
        ["bash", str(ENTRYPOINT), "printf", "ok"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert result.stdout == "ok"
