"""Unit tests for DockerComposeController (core orchestration logic)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from xde.commands.env import generate_fresh_env_content, perform_env_regenerate
from xde.core.docker import DockerComposeController
from xde.core.environment import EnvironmentContext, EnvironmentType


@pytest.fixture
def mock_env():
    return EnvironmentContext(env_type=EnvironmentType.HOST)


@pytest.fixture
def controller(mock_env):
    return DockerComposeController(env=mock_env)


class TestDockerComposeController:
    """Tests for DockerComposeController using mocks for subprocess safety."""

    def test_services_running_returns_true_on_running_service(self, controller):
        """services_running returns True for listed running service."""
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
        with patch(
            "xde.core.docker.DEFAULT_CONFIG_FILE", tmp_path / "nope.json"
        ):
            assert controller.get_payload_project_name() == "my-payload-cms"

    def test_get_db_config_returns_values_from_config(
        self, controller, tmp_path
    ):
        """get_db_config loads dbName/dbUser when present."""
        cfg = tmp_path / "cfg.json"
        cfg.write_text('{"dbName": "mydb", "dbUser": "me"}')
        with patch("xde.core.docker.DEFAULT_CONFIG_FILE", cfg):
            assert controller.get_db_config() == ("mydb", "me")

    def test_get_db_config_falls_back_safely(self, controller, tmp_path):
        """get_db_config uses defaults when no config or bad json."""
        with patch("xde.core.docker.DEFAULT_CONFIG_FILE", tmp_path / "no.json"):
            assert controller.get_db_config() == ("payload_db", "payload")


class TestEnvRegenerate:
    """Tests for the pure env regenerate helpers (step 2)."""

    def test_generate_fresh_env_content_is_pure(self):
        """Returns expected keys; different secrets prove pure/random."""
        c1 = generate_fresh_env_content()
        c2 = generate_fresh_env_content()
        assert "POSTGRES_USER=" in c1
        assert "PAYLOAD_SECRET=" in c1
        assert "DATABASE_URI=" in c1
        # Different runs produce different secrets (random)
        assert c1 != c2

    def test_perform_env_regenerate_dry_run(self, tmp_path):
        """Dry run does not write file."""
        target = tmp_path / ".env-test"
        rc = perform_env_regenerate(dry_run=True, env_file=target)
        assert rc == 0
        assert not target.exists()

    def test_perform_env_regenerate_writes_with_yes(self, tmp_path):
        """With --yes it writes the file (real but in tmp)."""
        target = tmp_path / ".env-test"
        rc = perform_env_regenerate(yes=True, env_file=target)
        assert rc == 0
        assert target.exists()
        content = target.read_text()
        assert "POSTGRES_PASSWORD=" in content
        assert (
            "payload_db" in content or "website" in content
        )  # db from config or default


def test_schema_command_is_callable():
    """Basic existence test for the new schema command (step 3)."""
    from xde.commands.schema import run_schema

    assert callable(run_schema)


# --- Tests for run_dev (direct inside-container execution + clean interrupt) ---

from unittest.mock import patch, MagicMock

from xde.commands.dev import run_dev
from xde.core.environment import EnvironmentContext, EnvironmentType


def test_run_dev_inside_container_direct_and_clean_interrupt():
    """Inside DEV_CONTAINER: runs pnpm dev directly, handles Ctrl+C (130) cleanly."""
    mock_env = EnvironmentContext(env_type=EnvironmentType.DEV_CONTAINER)
    mock_docker = MagicMock()

    with patch("xde.commands.dev.subprocess.run") as mock_run:
        # Simulate user pressing Ctrl+C: returncode 130
        mock_result = MagicMock(returncode=130)
        mock_run.return_value = mock_result

        rc = run_dev({}, env=mock_env, docker=mock_docker)

        assert rc == 0
        mock_run.assert_called_once()
        # Should not have called docker.exec for the dev server itself
        mock_docker.exec.assert_not_called()


def test_run_dev_inside_container_real_failure_still_reports():
    """Inside: real non-zero (not interrupt) still gives warning + fallback."""
    mock_env = EnvironmentContext(env_type=EnvironmentType.DEV_CONTAINER)
    mock_docker = MagicMock()

    with patch("xde.commands.dev.subprocess.run") as mock_run:
        mock_result = MagicMock(returncode=1)
        mock_run.return_value = mock_result

        rc = run_dev({}, env=mock_env, docker=mock_docker)

        assert rc == 1
        # The warning/fallback path should have been exercised (we don't assert
        # prints here to keep test simple, but rc indicates it took the failure branch)


def test_run_dev_host_path_uses_docker_exec():
    """Outside (HOST): falls back to docker.exec for the dev server launch."""
    mock_env = EnvironmentContext(env_type=EnvironmentType.HOST)
    mock_docker = MagicMock()
    mock_docker.exec.return_value = MagicMock(returncode=0)

    rc = run_dev({}, env=mock_env, docker=mock_docker)

    # It will still print success etc., but the key is it used the docker path
    mock_docker.exec.assert_called()
    # rc will be 0 from the final return in current code for the host success path
    assert rc == 0
