"""Unit tests for host-conditional Git DX detection helpers."""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HOST_FS = REPO_ROOT / ".devcontainer" / "scripts" / "lib" / "host-fs.sh"
CONFIGURE = REPO_ROOT / ".devcontainer" / "scripts" / "configure-git-dx.sh"


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


pytestmark = pytest.mark.skipif(
    not _bash_available(),
    reason="usable bash required for Git DX shell helpers",
)


def _bash(
    script: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        ["bash", "-c", script],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=merged,
    )


def test_friction_fstype_detects_9p() -> None:
    script = textwrap.dedent(
        f"""
        set -euo pipefail
        source "{HOST_FS.as_posix()}"
        xgic_is_friction_fstype 9p
        """
    )
    result = _bash(script)
    assert result.returncode == 0, result.stderr


def test_friction_fstype_rejects_ext4() -> None:
    script = textwrap.dedent(
        f"""
        set -euo pipefail
        source "{HOST_FS.as_posix()}"
        if xgic_is_friction_fstype ext4; then
          exit 1
        fi
        exit 0
        """
    )
    result = _bash(script)
    assert result.returncode == 0, result.stderr


def test_needs_safe_directory_when_hint_windows(
    tmp_path: Path,
) -> None:
    mounts = tmp_path / "mounts"
    mounts.write_text(
        "/dev/sda1 / ext4 rw,relatime 0 0\n",
        encoding="utf-8",
    )
    ws = tmp_path / "workspace"
    ws.mkdir()
    script = textwrap.dedent(
        f"""
        set -euo pipefail
        source "{HOST_FS.as_posix()}"
        xgic_needs_git_safe_directory
        """
    )
    result = _bash(
        script,
        env={
            "XGIC_DOCKER_HOST_OS": "windows",
            "XGIC_WORKSPACE": str(ws),
            "XGIC_PROC_MOUNTS": str(mounts),
        },
    )
    assert result.returncode == 0, result.stderr


def test_mount_prefix_does_not_false_match(tmp_path: Path) -> None:
    ws = tmp_path / "workspace"
    ws.mkdir()
    mounts = tmp_path / "mounts"
    # /work must not match /workspace; only exact /workspace 9p should.
    mounts.write_text(
        "\n".join(
            [
                "other /work 9p rw,sync 0 0",
                f"hostshare {ws.as_posix()} ext4 rw,relatime 0 0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    script = textwrap.dedent(
        f"""
        set -euo pipefail
        findmnt() {{ return 1; }}
        source "{HOST_FS.as_posix()}"
        ft="$(xgic_workspace_fstype)"
        test "$ft" = "ext4"
        """
    )
    result = _bash(
        script,
        env={
            "XGIC_WORKSPACE": str(ws),
            "XGIC_PROC_MOUNTS": str(mounts),
        },
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_needs_safe_directory_when_9p_mount(tmp_path: Path) -> None:
    ws = tmp_path / "workspace"
    ws.mkdir()
    mounts = tmp_path / "mounts"
    mounts.write_text(
        f"hostshare {ws.as_posix()} 9p rw,sync 0 0\n",
        encoding="utf-8",
    )
    script = textwrap.dedent(
        f"""
        set -euo pipefail
        # Force findmnt off so /proc override is used.
        findmnt() {{ return 1; }}
        source "{HOST_FS.as_posix()}"
        xgic_needs_git_safe_directory
        """
    )
    result = _bash(
        script,
        env={
            "XGIC_DOCKER_HOST_OS": "",
            "XGIC_WORKSPACE": str(ws),
            "XGIC_PROC_MOUNTS": str(mounts),
        },
    )
    assert result.returncode == 0, result.stderr


def test_linux_hint_skips_without_friction_fs(tmp_path: Path) -> None:
    ws = tmp_path / "workspace"
    ws.mkdir()
    # Match ownership to current user so mismatch signal is false.
    mounts = tmp_path / "mounts"
    mounts.write_text(
        f"/dev/sda1 {ws.as_posix()} ext4 rw,relatime 0 0\n",
        encoding="utf-8",
    )
    script = textwrap.dedent(
        f"""
        set -euo pipefail
        findmnt() {{ return 1; }}
        source "{HOST_FS.as_posix()}"
        if xgic_needs_git_safe_directory; then
          exit 1
        fi
        exit 0
        """
    )
    result = _bash(
        script,
        env={
            "XGIC_DOCKER_HOST_OS": "linux",
            "XGIC_WORKSPACE": str(ws),
            "XGIC_PROC_MOUNTS": str(mounts),
        },
    )
    assert result.returncode == 0, result.stderr


def test_configure_status_runs() -> None:
    result = subprocess.run(
        ["bash", str(CONFIGURE), "--status"],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "needs_safe_directory=" in result.stdout


def test_configure_quiet_is_silent_when_safe_directory_not_needed(
    tmp_path: Path,
) -> None:
    ws = tmp_path / "workspace"
    ws.mkdir()
    mounts = tmp_path / "mounts"
    mounts.write_text(
        f"/dev/sda1 {ws.as_posix()} ext4 rw,relatime 0 0\n",
        encoding="utf-8",
    )
    home = tmp_path / "home"
    home.mkdir()
    # Pre-seed so known_hosts / insteadOf are no-ops (quiet = no stdout).
    ssh = home / ".ssh"
    ssh.mkdir()
    (ssh / "known_hosts").write_text(
        "github.com ssh-ed25519 "
        "AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl\n",
        encoding="utf-8",
    )
    gitconfig = home / "gitconfig"
    gitconfig.write_text(
        "[url \"https://github.com/\"]\n"
        "\tinsteadOf = git@github.com:\n"
        "\tinsteadOf = ssh://git@github.com/\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "XGIC_DOCKER_HOST_OS": "linux",
            "XGIC_WORKSPACE": str(ws),
            "XGIC_PROC_MOUNTS": str(mounts),
            "XGIC_GIT_DX_VERBOSE": "0",
            "XGIC_GIT_PREFER_HTTPS": "1",
            "GIT_CONFIG_GLOBAL": str(gitconfig),
            "GIT_CONFIG_NOSYSTEM": "1",
        }
    )
    result = subprocess.run(
        ["bash", str(CONFIGURE), "--quiet"],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert result.stdout.strip() == ""
    assert "Skipping safe.directory" not in result.stdout
    assert "needs_safe_directory=" not in result.stdout


def test_configure_seeds_known_hosts_and_https_insteadof(tmp_path: Path) -> None:
    ws = tmp_path / "workspace"
    ws.mkdir()
    mounts = tmp_path / "mounts"
    mounts.write_text(
        f"/dev/sda1 {ws.as_posix()} ext4 rw,relatime 0 0\n",
        encoding="utf-8",
    )
    home = tmp_path / "home"
    home.mkdir()
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "XGIC_DOCKER_HOST_OS": "linux",
            "XGIC_WORKSPACE": str(ws),
            "XGIC_PROC_MOUNTS": str(mounts),
            "XGIC_GIT_PREFER_HTTPS": "1",
            "GIT_CONFIG_GLOBAL": str(home / "gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "1",
        }
    )
    result = subprocess.run(
        ["bash", str(CONFIGURE), "--quiet"],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    kh = home / ".ssh" / "known_hosts"
    assert kh.is_file()
    assert "github.com ssh-ed25519" in kh.read_text(encoding="utf-8")
    cfg = subprocess.run(
        ["git", "config", "--global", "--get-regexp", r"^url\..*\.insteadof$"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert cfg.returncode == 0, cfg.stderr
    assert "https://github.com/" in cfg.stdout
    assert "git@github.com:" in cfg.stdout
