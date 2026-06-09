"""Pytest fixtures for xde integration tests (rec5).

Provides reusable temp config and project setup helpers that can
later drive real (or docker-compose test profile) targeted up +
project creation flows without duplicating logic from unit tests.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def temp_create_payload_config(tmp_path: Path) -> Path:
    """Write a minimal create-payload-config.json and return its path.

    Tests can monkeypatch xde.core.docker.DEFAULT_CONFIG_FILE or
    xde.core.project.DEFAULT_CONFIG_FILE to point here.
    """
    cfg = {
        "projectName": "integration-test-app",
        "template": "blank",
        "dbAdapter": "postgres",
        "dbName": "test_db",
        "dbUser": "test",
        "agent": "none",
    }
    p = tmp_path / "create-payload-config.json"
    p.write_text(json.dumps(cfg, indent=2))
    return p


@pytest.fixture
def temp_project_root(tmp_path: Path) -> Path:
    """A clean temp dir to act as the 'workspace' root for project ensure."""
    return tmp_path / "workspace"
