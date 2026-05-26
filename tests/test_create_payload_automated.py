"""Unit tests for create-payload-automated.py logic."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Import the functions we want to test.
# We load the script as a module using importlib because the filename
# contains hyphens (create-payload-automated.py), which are not valid in Python identifiers.
import importlib.util
import sys
from pathlib import Path

script_path = Path(__file__).parent.parent / ".devcontainer" / "scripts" / "create-payload-automated.py"
spec = importlib.util.spec_from_file_location("create_payload_automated", script_path)
create_payload_automated = importlib.util.module_from_spec(spec)
sys.modules["create_payload_automated"] = create_payload_automated
spec.loader.exec_module(create_payload_automated)

load_config = create_payload_automated.load_config
merge_config = create_payload_automated.merge_config
build_command = create_payload_automated.build_command
_project_has_payload_config = create_payload_automated._project_has_payload_config
DEFAULT_CONFIG = create_payload_automated.DEFAULT_CONFIG


class TestLoadConfig:
    def test_loads_defaults_when_no_config_file(self, mock_env, temp_project_dir):
        config_path = temp_project_dir / "nonexistent.json"
        result = load_config(config_path)
        assert result["projectName"] == DEFAULT_CONFIG["projectName"]
        assert result["template"] == DEFAULT_CONFIG["template"]

    def test_loads_from_json_file(self, mock_env, temp_project_dir, sample_config):
        """Even with the fixture cleaning the env, a JSON file with dbUri should be respected."""
        config_path = temp_project_dir / "config.json"
        config_path.write_text(json.dumps(sample_config))

        result = load_config(config_path)
        assert result["projectName"] == "test-payload-app"
        assert result["dbUri"] == sample_config["dbUri"]

    def test_database_uri_env_always_overrides_config_when_valid(self, mock_env, temp_project_dir, sample_config):
        """A valid DATABASE_URI from the environment should take precedence over the JSON file.
        This is important for devcontainer setups where the live connection string comes from compose.
        """
        mock_env.setenv("DATABASE_URI", "postgres://env:pass@host/db")

        config_path = temp_project_dir / "config.json"
        config_path.write_text(json.dumps(sample_config))

        result = load_config(config_path)
        # Env var should win even if the JSON had a dbUri
        assert result["dbUri"] == "postgres://env:pass@host/db"

    def test_handles_invalid_json_gracefully(self, temp_project_dir, caplog):
        config_path = temp_project_dir / "bad.json"
        config_path.write_text("{ invalid json }")

        result = load_config(config_path)
        assert result["projectName"] == DEFAULT_CONFIG["projectName"]  # falls back to default
        assert "Failed to load config file" in caplog.text


class TestMergeConfig:
    def test_cli_overrides_config(self, sample_config):
        class Args:
            name = "cli-project"
            template = "ecommerce"
            db_adapter = "mongodb"
            db_uri = "mongodb://localhost/test"

        result = merge_config(Args(), sample_config)

        assert result["projectName"] == "cli-project"
        assert result["template"] == "ecommerce"
        assert result["dbAdapter"] == "mongodb"
        assert result["dbUri"] == "mongodb://localhost/test"

    def test_none_values_do_not_override(self, sample_config):
        class Args:
            name = None
            template = None
            db_adapter = None
            db_uri = None

        result = merge_config(Args(), sample_config)
        assert result["projectName"] == sample_config["projectName"]

    @pytest.mark.parametrize(
        "field,cli_value,expected",
        [
            ("name", "my-cool-app", "my-cool-app"),
            ("template", "blank", "blank"),
            ("db_adapter", "sqlite", "sqlite"),
            ("db_uri", "postgres://custom/db", "postgres://custom/db"),
        ],
    )
    def test_individual_cli_overrides(self, sample_config, field, cli_value, expected):
        class Args:
            name = None
            template = None
            db_adapter = None
            db_uri = None

        setattr(Args, field, cli_value)
        result = merge_config(Args(), sample_config)
        key = "projectName" if field == "name" else "dbAdapter" if field == "db_adapter" else "dbUri" if field == "db_uri" else field
        assert result[key] == expected


class TestBuildCommand:
    def test_builds_basic_command(self, sample_config):
        cmd = build_command(sample_config)
        assert "pnpx" in cmd
        assert "create-payload-app@latest" in cmd
        assert "-n" in cmd
        assert "test-payload-app" in cmd
        assert "-t" in cmd
        assert "website" in cmd
        assert "--no-agent" in cmd
        assert "--use-pnpm" in cmd

    def test_respects_use_pnpm_flag(self):
        config = {"projectName": "test", "usePnpm": False}
        cmd = build_command(config)
        assert "--use-pnpm" not in cmd

    @pytest.mark.parametrize(
        "config_overrides,expected_flags",
        [
            ({}, ["-n", "test-payload-app", "-t", "website", "--no-agent", "--use-pnpm"]),
            ({"usePnpm": False}, ["-n", "test-payload-app", "-t", "website", "--no-agent"]),
            ({"agent": None}, ["-n", "test-payload-app", "-t", "website", "--use-pnpm"]),
            ({"template": "blank"}, ["-n", "test-payload-app", "-t", "blank", "--no-agent", "--use-pnpm"]),
        ],
    )
    def test_build_command_variations(self, sample_config, config_overrides, expected_flags):
        config = {**sample_config, **config_overrides}
        cmd = build_command(config)
        for flag in expected_flags:
            assert flag in cmd


class TestProjectHasPayloadConfig:
    def test_detects_payload_config_ts(self, temp_project_dir):
        (temp_project_dir / "payload.config.ts").touch()
        assert _project_has_payload_config(temp_project_dir) is True

    def test_detects_payload_config_js(self, temp_project_dir):
        (temp_project_dir / "payload.config.js").touch()
        assert _project_has_payload_config(temp_project_dir) is True

    def test_detects_in_subdirectory(self, temp_project_dir):
        subdir = temp_project_dir / "my-app"
        subdir.mkdir()
        (subdir / "payload.config.ts").touch()
        assert _project_has_payload_config(temp_project_dir) is True

    def test_returns_false_when_no_config(self, temp_project_dir):
        assert _project_has_payload_config(temp_project_dir) is False

    def test_ignores_non_payload_files(self, temp_project_dir):
        (temp_project_dir / "package.json").touch()
        (temp_project_dir / "payload.config.bak").touch()
        assert _project_has_payload_config(temp_project_dir) is False


class TestLoadConfigAdditional:
    def test_partial_config_merges_with_defaults(self, temp_project_dir):
        config_path = temp_project_dir / "partial.json"
        config_path.write_text(json.dumps({"projectName": "partial-project"}))

        result = load_config(config_path)
        assert result["projectName"] == "partial-project"
        assert result["template"] == DEFAULT_CONFIG["template"]  # should keep default

    def test_env_var_only_no_config_file(self, mock_env, temp_project_dir):
        import os
        os.environ["DATABASE_URI"] = "postgres://only-env/db"

        config_path = temp_project_dir / "nonexistent.json"
        result = load_config(config_path)
        assert result["dbUri"] == "postgres://only-env/db"

    def test_missing_database_uri_raises_in_wizard(self, temp_project_dir, sample_config):
        """Ensure run_payload_wizard fails cleanly when no dbUri is present."""
        from create_payload_automated import run_payload_wizard

        bad_config = {**sample_config, "dbUri": None}

        with pytest.raises(SystemExit):
            run_payload_wizard(bad_config, temp_project_dir)


# =============================================================================
# Mocked Integration-style tests for the orchestration layer
# =============================================================================

class TestRunPayloadWizardMocked:
    """Higher-level tests that mock pexpect to avoid real process spawning."""

    def test_skips_when_project_already_exists(self, temp_project_dir, sample_config, caplog):
        (temp_project_dir / "payload.config.ts").touch()

        # Ensure the logger level is high enough to capture INFO messages
        caplog.set_level("INFO")

        from create_payload_automated import run_payload_wizard
        run_payload_wizard(sample_config, temp_project_dir, dry_run=False)

        assert "already exists" in caplog.text.lower()

    def test_dry_run_does_not_spawn(self, temp_project_dir, sample_config, mocker):
        from create_payload_automated import run_payload_wizard
        mock_spawn = mocker.patch("create_payload_automated.pexpect.spawn")

        run_payload_wizard(sample_config, temp_project_dir, dry_run=True)

        mock_spawn.assert_not_called()

    def test_successful_wizard_run_with_mocked_pexpect(self, temp_project_dir, sample_config, mocker):
        """Test the happy path by injecting a mock spawn callable."""
        from create_payload_automated import run_payload_wizard

        mock_child = MagicMock()
        mock_child.expect.side_effect = [None, None, None, None, None]  # Simulate successful prompt sequence
        mock_child.exitstatus = 0

        def fake_spawn(*args, **kwargs):
            return mock_child

        run_payload_wizard(sample_config, temp_project_dir, spawn=fake_spawn)

        # Verify key interactions
        assert mock_child.send.call_count >= 3  # down arrow, enter, ctrl+u, data, enter
        mock_child.expect.assert_called()  # At least some expects happened
        mock_child.close.assert_called()

    def test_timeout_during_wizard_is_handled(self, temp_project_dir, sample_config, mocker, caplog):
        from create_payload_automated import run_payload_wizard
        import pexpect

        mock_child = MagicMock()
        mock_child.expect.side_effect = pexpect.TIMEOUT("timeout")

        def fake_spawn(*args, **kwargs):
            return mock_child

        with pytest.raises(pexpect.TIMEOUT):
            run_payload_wizard(sample_config, temp_project_dir, spawn=fake_spawn)

        assert "Timeout waiting for expected prompt" in caplog.text
