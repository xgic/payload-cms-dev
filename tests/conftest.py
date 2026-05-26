"""Shared pytest fixtures for the automation tests."""

import pytest
from pathlib import Path
from unittest.mock import patch
import tempfile
import os


@pytest.fixture
def temp_project_dir():
    """Provide a temporary directory to simulate a project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Provide a sample configuration dictionary."""
    return {
        "projectName": "test-payload-app",
        "template": "website",
        "agent": "--no-agent",
        "dbAdapter": "postgres",
        "dbUri": "postgres://user:pass@localhost:5432/testdb",
        "usePnpm": True,
    }


@pytest.fixture
def mock_env(monkeypatch):
    """Provide a clean environment for testing config loading."""
    monkeypatch.delenv("DATABASE_URI", raising=False)
    return monkeypatch
