"""Unit tests for DockerComposeController (core orchestration logic)."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from xde.core.environment import EnvironmentContext, EnvironmentType
from xde.core.docker import DockerComposeController


@pytest.fixture
def mock_env():
    return EnvironmentContext(env_type=EnvironmentType.HOST)


@pytest.fixture
def controller(mock_env):
    return DockerComposeController(env=mock_env)


class TestDockerComposeController:
    """Tests for DockerComposeController using mocks for subprocess safety."""

    def test_services_running_returns_true_on_running_service(self, controller):
        """services_running should return True when main service is listed as running."""
        with patch.object(controller, "_run_compose") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = "xgic-payload-cms-dev-containers\nother"
            mock_run.return_value = mock_result
            assert controller.services_running() is True
            mock_run.assert_called_once()

    def test_services_running_returns_false_on_no_services(self, controller):
        """services_running should return False when no running services."""
        with patch.object(controller, "_run_compose") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = ""
            mock_run.return_value = mock_result
            assert controller.services_running() is False

    def test_up_calls_compose_with_detach(self, controller):
        """up() should call docker compose up -d (and --build if requested)."""
        with patch.object(controller, "_run_compose") as mock_run:
            controller.up()
            mock_run.assert_called_with("up", "-d")
            controller.up(build=True)
            mock_run.assert_called_with("up", "-d", "--build")

    def test_down_calls_compose_down(self, controller):
        with patch.object(controller, "_run_compose") as mock_run:
            controller.down()
            mock_run.assert_called_with("down")

    def test_db_ready_uses_pg_isready(self, controller):
        """db_ready should exec pg_isready in postgres container."""
        with patch.object(controller, "_run_compose") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            assert controller.db_ready() is True
            # Check it called exec -T postgres pg_isready ...
            args = mock_run.call_args[0]
            assert "exec" in args
            assert "postgres" in args
            assert "pg_isready" in args

    def test_remove_volume_calls_docker_volume_rm(self, controller):
        with patch.object(controller, "_run_compose") as mock_run:
            assert controller.remove_volume("test-volume") is True
            mock_run.assert_called_with("volume", "rm", "-f", "test-volume")

    def test_get_payload_project_name_falls_back(self, controller, tmp_path):
        """Falls back when no config."""
        # Point to non-existent config by patching
        with patch("xde.core.docker.DEFAULT_CONFIG_FILE", tmp_path / "nope.json"):
            assert controller.get_payload_project_name() == "my-payload-cms"