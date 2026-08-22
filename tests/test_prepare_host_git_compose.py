"""Unit tests for host Git Compose overlay generator."""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / ".devcontainer"
    / "scripts"
    / "prepare_host_git_compose.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "prepare_host_git_compose", SCRIPT
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_render_overlay_https_prefer_has_mode_env() -> None:
    mod = _load_module()
    text = mod.render_overlay(
        host_os="windows",
        kind="desktop",
        mode="https-prefer",
        ssh_auth_sock_env=None,
        mount_dd=False,
        mount_host_sock=None,
    )
    assert "XGIC_GIT_AUTH_MODE: https-prefer" in text
    assert "XGIC_DOCKER_HOST_OS: windows" in text
    assert "XGIC_DOCKER_HOST_KIND: desktop" in text
    assert "SSH_AUTH_SOCK:" not in text
    assert "volumes:" not in text


def test_render_overlay_desktop_agent_mounts_dd_sock() -> None:
    mod = _load_module()
    text = mod.render_overlay(
        host_os="windows",
        kind="desktop",
        mode="ssh-agent-desktop",
        ssh_auth_sock_env=mod.DD_SOCK,
        mount_dd=True,
        mount_host_sock=None,
    )
    assert "SSH_AUTH_SOCK: /run/host-services/ssh-auth.sock" in text
    assert "source: /run/host-services/ssh-auth.sock" in text
    assert "volumes:" in text


def test_render_overlay_host_agent_mounts_ssh_agent() -> None:
    mod = _load_module()
    text = mod.render_overlay(
        host_os="linux",
        kind="engine",
        mode="ssh-agent-host",
        ssh_auth_sock_env="/ssh-agent",
        mount_dd=False,
        mount_host_sock="/tmp/ssh-agent.sock",
    )
    assert "SSH_AUTH_SOCK: /ssh-agent" in text
    assert "source: /tmp/ssh-agent.sock" in text
    assert "target: /ssh-agent" in text
