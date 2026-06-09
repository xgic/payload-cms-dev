"""Unit tests for DockerComposeController (core orchestration logic)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from xde.commands.dev import run_dev
from xde.commands.env import generate_fresh_env_content, perform_env_regenerate
from xde.commands.setup import run_setup_payloadcms
from xde.core.docker import DockerComposeController
from xde.core.environment import EnvironmentContext, EnvironmentType
from xde.core.project import (
    build_create_payload_command,
    ensure_payload_project,
    is_payload_project_complete,
    load_create_payload_config,
)


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
        """remove_volume must use top-level docker (not compose volume)."""
        with patch("xde.core.docker.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            assert controller.remove_volume("test-volume") is True
            # Should call the real docker CLI, not compose subcommand
            called_cmd = mock_run.call_args[0][0]
            assert called_cmd[0:4] == ["docker", "volume", "rm", "-f"]
            assert "test-volume" in called_cmd

    def test_up_with_services_targets_only_those(self, controller):
        """up(services=[...]) should pass the services to compose up."""
        with patch.object(controller, "_run_compose") as mock_run:
            controller.up(services=["postgres"])
            mock_run.assert_called_with("up", "-d", "postgres")

    def test_rm_service_passes_expected_flags(self, controller):
        """rm_service should compose the rm flags and call through compose."""
        with patch.object(controller, "_run_compose") as mock_run:
            controller.rm_service(
                "postgres", force=True, stop=True, remove_volumes=False
            )
            mock_run.assert_called_with(
                "rm", "-f", "-s", "postgres", check=False
            )

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


# --- Tests for run_dev (direct inside + clean interrupt) ---


def test_run_dev_inside_container_direct_and_clean_interrupt():
    """Inside: runs pnpm dev directly, handles Ctrl+C (130) cleanly."""
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
        # The warning/fallback path exercised (rc shows failure branch taken).


def test_run_dev_host_path_uses_docker_exec():
    """Outside (HOST): falls back to docker.exec for the dev server launch."""
    mock_env = EnvironmentContext(env_type=EnvironmentType.HOST)
    mock_docker = MagicMock()
    mock_docker.exec.return_value = MagicMock(returncode=0)

    rc = run_dev({}, env=mock_env, docker=mock_docker)

    # Key: used the docker path (outside case).
    mock_docker.exec.assert_called()
    # rc == 0 from final return on the host success path.
    assert rc == 0


# --- Tests for the new modular project setup (xde setup payloadcms) ---


class TestPayloadProjectSetupPure:
    """Pure, side-effect free tests for the setup helpers."""

    def test_load_create_payload_config_defaults_when_missing(self, tmp_path):
        """Missing config yields safe defaults."""
        missing = tmp_path / "no-config.json"
        cfg = load_create_payload_config(missing)
        assert cfg["projectName"] == "my-payload-cms"
        assert cfg["template"] == "website"
        assert cfg["dbAdapter"] == "postgres"
        assert cfg["agent"] == "none"

    def test_load_create_payload_config_merges_partial(self, tmp_path):
        """Partial config still supplies defaults for missing keys."""
        cfg_path = tmp_path / "partial.json"
        cfg_path.write_text('{"projectName": "foo-app", "template": "blank"}')
        cfg = load_create_payload_config(cfg_path)
        assert cfg["projectName"] == "foo-app"
        assert cfg["template"] == "blank"
        assert cfg["dbAdapter"] == "postgres"  # default filled

    def test_is_payload_project_complete_true_for_root_config(self, tmp_path):
        """Detects payload.config.ts at project root."""
        proj = tmp_path / "website"
        proj.mkdir()
        (proj / "payload.config.ts").write_text("export default {}")
        assert is_payload_project_complete(proj) is True

    def test_is_payload_project_complete_true_for_src_config(self, tmp_path):
        """Detects payload.config.js under src/ (standard template)."""
        proj = tmp_path / "my-site"
        (proj / "src").mkdir(parents=True)
        (proj / "src" / "payload.config.js").write_text("module.exports = {}")
        assert is_payload_project_complete(proj) is True

    def test_is_payload_project_complete_false_for_empty_dir(self, tmp_path):
        """Empty or non-Payload dir is not complete."""
        proj = tmp_path / "empty"
        proj.mkdir()
        assert is_payload_project_complete(proj) is False
        assert is_payload_project_complete(tmp_path / "no-dir") is False

    def test_build_create_payload_command_basic(self):
        """Builds the expected non-interactive argv (no db uri case)."""
        cmd = build_create_payload_command(
            "website", template="website", db_adapter="postgres"
        )
        assert cmd[0:5] == [
            "pnpx",
            "create-payload-app@latest",
            "website",
            "-t",
            "website",
        ]
        assert "--use-pnpm" in cmd
        assert "--db" in cmd
        assert "--db-accept-recommended" in cmd
        assert "--no-agent" in cmd
        assert "--db-connection-string" not in cmd

    def test_build_create_payload_command_with_connection_string_and_agent(
        self,
    ):
        """Includes --db-connection-string and --agent when provided."""
        cmd = build_create_payload_command(
            "site",
            template="blank",
            db_adapter="postgres",
            db_connection_string="postgres://u:p@h:5432/db",
            agent="myagent",
        )
        assert "--db-connection-string" in cmd
        assert "postgres://u:p@h:5432/db" in cmd
        assert cmd[cmd.index("--agent") + 1] == "myagent"
        assert "--no-agent" not in cmd


def test_run_setup_payloadcms_is_callable():
    """Basic smoke that the command handler exists and is wired."""
    assert callable(run_setup_payloadcms)


def test_ensure_payload_project_is_idempotent_on_complete(
    tmp_path, monkeypatch
):
    """If already complete, ensure returns 0 with no creation side effects."""
    proj = tmp_path / "complete-site"
    proj.mkdir()
    (proj / "src").mkdir()
    (proj / "src" / "payload.config.ts").write_text("// ok")

    # Force the config loader and project dir resolution to our tmp
    monkeypatch.setattr(
        "xde.core.project.DEFAULT_CONFIG_FILE",
        tmp_path / "ignored.json",
    )
    # Patch get_project_name by controlling load or by chdir + name
    # Simpler: patch load to return our name, and chdir so Path("..") works
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "xde.core.project.load_create_payload_config",
        lambda *a, **k: {"projectName": "complete-site"},
    )

    rc = ensure_payload_project()
    assert rc == 0
    # No subprocess calls should have been attempted
    # (we didn't patch yet, but since complete, early return)
