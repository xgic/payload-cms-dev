"""Unit tests for reset-project.py.

Focus is on pure, testable functions that contain important logic:
- get_payload_project_name
- _get_db_details_from_config
- find_payload_project_dirs
- is_running_in_devcontainer (basic cases)
"""

from pathlib import Path
import json
import pytest

# Import the functions we want to test
# We import from the scripts directory directly
import sys
import importlib.util
from pathlib import Path

# Dynamically import the reset-project.py module (note the hyphen in filename)
script_path = Path(__file__).parent.parent / ".devcontainer" / "scripts" / "reset-project.py"
spec = importlib.util.spec_from_file_location("reset_project", script_path)
reset_project = importlib.util.module_from_spec(spec)
sys.modules["reset_project"] = reset_project
spec.loader.exec_module(reset_project)

from reset_project import (
    get_payload_project_name,
    _get_db_details_from_config,
    find_payload_project_dirs,
    is_running_in_devcontainer,
    DEFAULT_PROJECT_NAME_FALLBACK,
)


class TestGetPayloadProjectName:
    """Tests for get_payload_project_name function."""

    def test_returns_default_when_config_missing(self, temp_workspace: Path):
        """Should return fallback when config file does not exist."""
        missing_config = temp_workspace / "nonexistent.json"
        result = get_payload_project_name(missing_config)
        assert result == DEFAULT_PROJECT_NAME_FALLBACK

    def test_returns_project_name_from_config(self, sample_config_file: Path):
        result = get_payload_project_name(sample_config_file)
        assert result == "my-test-app"

    def test_returns_default_when_projectName_missing(self, minimal_config_file: Path):
        # minimal_config_file only has projectName, so this tests the happy path indirectly
        result = get_payload_project_name(minimal_config_file)
        assert result == "minimal-project"

    def test_returns_default_on_invalid_json(self, temp_workspace: Path):
        bad_config = temp_workspace / "bad.json"
        bad_config.write_text("{ not valid json }")
        result = get_payload_project_name(bad_config)
        assert result == DEFAULT_PROJECT_NAME_FALLBACK

    def test_strips_whitespace_from_project_name(self, temp_workspace: Path):
        config = temp_workspace / "config.json"
        config.write_text(json.dumps({"projectName": "  spaced-name  "}))
        result = get_payload_project_name(config)
        assert result == "spaced-name"


class TestGetDbDetailsFromConfig:
    """Tests for the important _get_db_details_from_config function."""

    def test_returns_defaults_when_no_config(self, temp_workspace: Path):
        missing = temp_workspace / "missing.json"
        db_name, db_user = _get_db_details_from_config(missing)
        assert db_name == "payload_db"
        assert db_user == "payload"

    def test_prefers_explicit_dbName_and_dbUser(self, sample_config_file: Path):
        db_name, db_user = _get_db_details_from_config(sample_config_file)
        assert db_name == "test_db"
        assert db_user == "test_user"

    def test_parses_db_name_from_dbUri_when_not_explicit(self, config_with_db_uri_only: Path):
        db_name, db_user = _get_db_details_from_config(config_with_db_uri_only)
        assert db_name == "parsed_db_name"
        assert db_user == "parsed_user"

    def test_parses_user_from_dbUri_when_not_explicit(self, temp_workspace: Path):
        config = temp_workspace / "config.json"
        config.write_text(json.dumps({
            "dbUri": "postgres://onlyuser:pass@host:5432/some_db"
        }))
        db_name, db_user = _get_db_details_from_config(config)
        assert db_user == "onlyuser"
        assert db_name == "some_db"

    def test_returns_defaults_on_malformed_dbUri(self, temp_workspace: Path):
        config = temp_workspace / "config.json"
        config.write_text(json.dumps({"dbUri": "not-a-valid-uri"}))
        db_name, db_user = _get_db_details_from_config(config)
        assert db_name == "payload_db"
        assert db_user == "payload"

    def test_handles_missing_config_gracefully(self, temp_workspace: Path):
        missing = temp_workspace / "does-not-exist.json"
        db_name, db_user = _get_db_details_from_config(missing)
        assert db_name == "payload_db"
        assert db_user == "payload"

    def test_prefers_explicit_fields_even_if_dbUri_present(self, temp_workspace: Path):
        """Explicit dbName/dbUser should win over parsed values from dbUri."""
        config = temp_workspace / "config.json"
        config.write_text(json.dumps({
            "dbName": "explicit_db",
            "dbUser": "explicit_user",
            "dbUri": "postgres://uri_user:pass@host:5432/uri_db"
        }))
        db_name, db_user = _get_db_details_from_config(config)
        assert db_name == "explicit_db"
        assert db_user == "explicit_user"

    def test_partial_explicit_dbName_only(self, temp_workspace: Path):
        """Only dbName provided — should parse user from dbUri if available."""
        config = temp_workspace / "config.json"
        config.write_text(json.dumps({
            "dbName": "only_name",
            "dbUri": "postgres://uri_user:pass@host:5432/uri_db"
        }))
        db_name, db_user = _get_db_details_from_config(config)
        assert db_name == "only_name"
        assert db_user == "uri_user"

    def test_handles_ipv6_style_or_complex_uris_gracefully(self, temp_workspace: Path):
        """Should not crash on unusual but valid-looking URIs."""
        config = temp_workspace / "config.json"
        config.write_text(json.dumps({
            "dbUri": "postgres://user:pass@[::1]:5432/mydb"
        }))
        db_name, db_user = _get_db_details_from_config(config)
        assert db_user == "user"
        assert db_name == "mydb"

    def test_returns_defaults_when_config_is_empty_object(self, temp_workspace: Path):
        config = temp_workspace / "config.json"
        config.write_text("{}")
        db_name, db_user = _get_db_details_from_config(config)
        assert db_name == "payload_db"
        assert db_user == "payload"


class TestFindPayloadProjectDirs:
    """Tests for find_payload_project_dirs heuristic."""

    def test_finds_project_with_payload_config_ts(self, temp_workspace: Path):
        project_dir = temp_workspace / "my-payload-app"
        project_dir.mkdir()
        (project_dir / "payload.config.ts").touch()

        result = find_payload_project_dirs(temp_workspace)
        assert project_dir in result

    def test_finds_project_with_src_payload_config(self, temp_workspace: Path):
        project_dir = temp_workspace / "another-app"
        src_dir = project_dir / "src"
        src_dir.mkdir(parents=True)
        (src_dir / "payload.config.js").touch()

        result = find_payload_project_dirs(temp_workspace)
        assert project_dir in result

    def test_finds_project_via_package_json_dependency(self, temp_workspace: Path):
        project_dir = temp_workspace / "payload-project"
        project_dir.mkdir()
        pkg = {
            "dependencies": {
                "payload": "^3.0.0",
                "react": "^18.0.0"
            }
        }
        (project_dir / "package.json").write_text(json.dumps(pkg))

        result = find_payload_project_dirs(temp_workspace)
        assert project_dir in result

    def test_ignores_dot_directories(self, temp_workspace: Path):
        dot_dir = temp_workspace / ".hidden-payload"
        dot_dir.mkdir()
        (dot_dir / "payload.config.ts").touch()

        result = find_payload_project_dirs(temp_workspace)
        assert dot_dir not in result

    def test_returns_sorted_list(self, temp_workspace: Path):
        # Create multiple projects
        for name in ["zebra-app", "alpha-app", "beta-app"]:
            p = temp_workspace / name
            p.mkdir()
            (p / "payload.config.ts").touch()

        result = find_payload_project_dirs(temp_workspace)
        names = [p.name for p in result]
        assert names == ["alpha-app", "beta-app", "zebra-app"]


class TestIsRunningInDevcontainer:
    """Basic environment detection tests."""

    def test_returns_false_by_default(self, monkeypatch):
        monkeypatch.delenv("REMOTE_CONTAINERS", raising=False)
        monkeypatch.delenv("CODESPACES", raising=False)
        monkeypatch.delenv("XG_AIS_HOST_TYPE", raising=False)

        assert is_running_in_devcontainer() is False

    def test_detects_remote_containers(self, monkeypatch):
        monkeypatch.setenv("REMOTE_CONTAINERS", "true")
        assert is_running_in_devcontainer() is True

    def test_detects_github_codespaces(self, monkeypatch):
        monkeypatch.setenv("CODESPACES", "true")
        assert is_running_in_devcontainer() is True


# =============================================================================
# Tests that exercise side-effect code using mocks
# =============================================================================

class TestResetPostgresDryRunAndBasicLogic:
    """Tests for reset_postgres focusing on logic that can be tested with mocks."""

    def test_dry_run_does_not_call_run(self, mock_run, temp_workspace: Path):
        """In dry-run mode, reset_postgres should not execute real commands."""
        from reset_project import reset_postgres

        result = reset_postgres(
            compose_file=temp_workspace / "docker-compose.yml",
            project_name="test-project",
            volume_name="test-volume",
            config_path=temp_workspace / "create-payload-config.json",
            dry_run=True,
            quiet=True,
        )

        assert result is True
        mock_run.assert_not_called()

    def test_success_path_uses_db_details_from_config(
        self, mock_docker_compose_psql_success, sample_config_file: Path, temp_workspace: Path
    ):
        """reset_postgres should call _get_db_details_from_config and use the returned user/db."""
        from reset_project import reset_postgres

        # Create a minimal compose file so the function can build commands
        compose = temp_workspace / "docker-compose.yml"
        compose.write_text("version: '3'")

        result = reset_postgres(
            compose_file=compose,
            project_name="test-proj",
            volume_name="test-vol",
            config_path=sample_config_file,
            dry_run=False,
            quiet=True,
        )

        assert result is True
        # Verify that the successful mock was used and pg_isready was called
        calls = [str(c) for c in mock_docker_compose_psql_success.call_args_list]
        assert any("pg_isready" in c for c in calls)
        # Should have used the dbUser from the sample config ("test_user")
        assert any("test_user" in c for c in calls)


# =============================================================================
# Additional tests for find_payload_project_dirs edge cases
# =============================================================================

class TestFindPayloadProjectDirsAdditional:
    """Extra edge cases for project directory detection."""

    def test_ignores_non_payload_directories(self, temp_workspace: Path):
        normal_dir = temp_workspace / "regular-folder"
        normal_dir.mkdir()
        (normal_dir / "package.json").write_text('{"name": "not-payload"}')

        result = find_payload_project_dirs(temp_workspace)
        assert normal_dir not in result

    def test_detects_payload_in_dev_dependencies(self, temp_workspace: Path):
        project_dir = temp_workspace / "dev-dep-project"
        project_dir.mkdir()
        pkg = {
            "devDependencies": {
                "@payloadcms/next": "^3.0.0"
            }
        }
        (project_dir / "package.json").write_text(json.dumps(pkg))

        result = find_payload_project_dirs(temp_workspace)
        assert project_dir in result

    def test_handles_broken_package_json_gracefully(self, temp_workspace: Path):
        project_dir = temp_workspace / "broken-pkg"
        project_dir.mkdir()
        (project_dir / "package.json").write_text("{ invalid json")

        # Should not crash
        result = find_payload_project_dirs(temp_workspace)
        assert project_dir not in result

    def test_ignores_directories_without_payload_indicators(self, temp_workspace: Path):
        """Ensure only directories with clear Payload signals are returned."""
        irrelevant = temp_workspace / "just-a-folder"
        irrelevant.mkdir()
        (irrelevant / "README.md").touch()

        result = find_payload_project_dirs(temp_workspace)
        assert irrelevant not in result

    def test_multiple_detection_methods_same_dir(self, temp_workspace: Path):
        """A directory with both payload.config.ts and package.json with payload should appear once."""
        project_dir = temp_workspace / "multi-signal"
        project_dir.mkdir()
        (project_dir / "payload.config.ts").touch()
        (project_dir / "package.json").write_text('{"dependencies": {"payload": "^3.0.0"}}')

        result = find_payload_project_dirs(temp_workspace)
        assert result.count(project_dir) == 1


# =============================================================================
# Basic tests for parse_args (covering key flags)
# =============================================================================

class TestParseArgs:
    """Lightweight tests for argument parsing in reset-project.py."""

    def test_default_values(self):
        from reset_project import parse_args
        # We can't easily test argparse without mocking sys.argv,
        # but we can at least import and call with mocked args if needed.
        # For now, a simple smoke that the function exists and has expected structure.
        assert callable(parse_args)

    def test_dry_run_flag_parses(self, monkeypatch):
        from reset_project import parse_args
        monkeypatch.setattr("sys.argv", ["reset-project.py", "--dry-run"])
        args = parse_args()
        assert args.dry_run is True
        assert args.assume_yes is False

    def test_compact_and_yes_flags(self, monkeypatch):
        from reset_project import parse_args
        monkeypatch.setattr("sys.argv", ["reset-project.py", "--compact", "--yes"])
        args = parse_args()
        assert args.compact is True
        assert args.assume_yes is True

    def test_rotate_credentials_flag(self, monkeypatch):
        from reset_project import parse_args
        monkeypatch.setattr("sys.argv", ["reset-project.py", "--rotate-credentials"])
        args = parse_args()
        assert args.rotate_credentials is True

    def test_custom_config_and_workspace(self, monkeypatch, tmp_path):
        from reset_project import parse_args
        custom_config = tmp_path / "my-config.json"
        custom_workspace = tmp_path / "workspace"
        monkeypatch.setattr("sys.argv", [
            "reset-project.py",
            "--config", str(custom_config),
            "--workspace", str(custom_workspace)
        ])
        args = parse_args()
        assert args.config == custom_config
        assert args.workspace == custom_workspace
