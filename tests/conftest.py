"""Pytest configuration and shared fixtures for devcontainer tooling tests."""

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Provide a clean temporary workspace directory."""
    return tmp_path


@pytest.fixture
def sample_config_file(temp_workspace: Path) -> Path:
    """Create a sample create-payload-config.json for testing."""
    config_path = temp_workspace / "create-payload-config.json"
    config = {
        "projectName": "my-test-app",
        "template": "website",
        "dbAdapter": "postgres",
        "dbName": "test_db",
        "dbUser": "test_user",
        "dbUri": "postgres://test_user:secret@postgres:5432/test_db",
        "adminEmail": "admin@example.com",
    }
    config_path.write_text(json.dumps(config, indent=2))
    return config_path


@pytest.fixture
def minimal_config_file(temp_workspace: Path) -> Path:
    """Create a minimal config with only projectName."""
    config_path = temp_workspace / "create-payload-config.json"
    config = {"projectName": "minimal-project"}
    config_path.write_text(json.dumps(config))
    return config_path


@pytest.fixture
def config_with_db_uri_only(temp_workspace: Path) -> Path:
    """Config that only has dbUri (tests fallback parsing)."""
    config_path = temp_workspace / "create-payload-config.json"
    config = {
        "projectName": "uri-only",
        "dbUri": "postgres://parsed_user:pass@host:5432/parsed_db_name?sslmode=require",
    }
    config_path.write_text(json.dumps(config))
    return config_path


# =============================================================================
# Fixtures for mocking side effects in reset-project.py
# =============================================================================


@pytest.fixture
def mock_run():
    """
    Provides a mock for the `run` function from reset_project.
    Useful for testing functions like reset_postgres without actually
    talking to Docker.
    """
    with patch("reset_project.run") as mock:
        # Default: make run() return a successful CompletedProcess
        mock.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        yield mock


@pytest.fixture
def mock_docker_compose_psql_success():
    """
    Pre-configured mock_run that simulates successful postgres operations
    (pg_isready and CREATE DATABASE).
    """

    def side_effect(cmd, **kwargs):
        cmd_str = " ".join(cmd)
        if "pg_isready" in cmd_str:
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout="ready", stderr=""
            )
        if "CREATE DATABASE" in cmd_str:
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout="", stderr=""
            )
        return subprocess.CompletedProcess(
            args=cmd, returncode=0, stdout="", stderr=""
        )

    with patch("reset_project.run", side_effect=side_effect) as mock:
        yield mock
