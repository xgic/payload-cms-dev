"""Unit tests for EnvironmentContext detection logic."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from xde.core.environment import EnvironmentContext, EnvironmentType


class TestEnvironmentDetection:
    """Tests for EnvironmentContext.detect()."""

    def test_detects_dev_container_via_remote_containers(self):
        """Should detect VS Code Dev Container when REMOTE_CONTAINERS=true."""
        with patch.dict(os.environ, {"REMOTE_CONTAINERS": "true"}, clear=True):
            ctx = EnvironmentContext.detect()
            assert ctx.env_type == EnvironmentType.DEV_CONTAINER
            assert ctx.is_remote is True

    def test_detects_dev_container_via_codespaces(self):
        """Should detect GitHub Codespaces."""
        with patch.dict(os.environ, {"CODESPACES": "true"}, clear=True):
            ctx = EnvironmentContext.detect()
            assert ctx.env_type == EnvironmentType.DEV_CONTAINER
            assert ctx.is_remote is True

    def test_detects_host_when_no_container_markers(self, tmp_path, monkeypatch):
        """Should default to HOST when no container environment variables are present."""
        # Ensure we're not inside a fake .devcontainer
        monkeypatch.chdir(tmp_path)
        with patch.dict(os.environ, {}, clear=True):
            ctx = EnvironmentContext.detect()
            assert ctx.env_type == EnvironmentType.HOST
            assert ctx.is_remote is False

    def test_is_host_only_command_safe_on_host(self):
        """Host environment should allow host-only commands."""
        ctx = EnvironmentContext(env_type=EnvironmentType.HOST)
        assert ctx.is_host_only_command_safe() is True

    def test_is_host_only_command_safe_in_dev_container(self):
        """Dev Container should not allow host-only commands."""
        ctx = EnvironmentContext(env_type=EnvironmentType.DEV_CONTAINER)
        assert ctx.is_host_only_command_safe() is False

    def test_describe_returns_human_readable_string(self):
        """describe() should return useful strings for logging/UI."""
        ctx = EnvironmentContext(env_type=EnvironmentType.DEV_CONTAINER)
        assert "Dev Container" in ctx.describe()