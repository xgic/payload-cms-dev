"""Example integration-style tests for project ensure + supporting services.

These use the temp config fixtures + monkeypatching to simulate
combined flows (e.g. ensure project after targeted postgres up).

Later can be extended with pytest-docker or real compose test
profiles to drive actual `docker compose up(services=["postgres"])` +
project creation (rec5).

Kept lightweight; heavy logic stays in unit tests.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from xde.core.project import ensure_payload_project


def test_ensure_payload_after_supporting_services(
    temp_create_payload_config: Path, temp_project_root: Path, monkeypatch
):
    """Simulated 'integration' of config-driven project ensure.

    In a fuller integration this would also exercise DockerComposeController
    .up(services=...) before/after. Here we focus on the project side
    using the shared fixtures.
    """
    # Point the project loader at our temp config (like real flows do)
    monkeypatch.setattr(
        "xde.core.project.DEFAULT_CONFIG_FILE", temp_create_payload_config
    )

    # Simulate incomplete project dir (post-reset scenario). Forces create path.
    app_dir = temp_project_root / "integration-test-app"
    app_dir.mkdir(parents=True)
    (app_dir / "README.md").write_text("partial")  # no payload.config.* marker

    monkeypatch.chdir(temp_project_root)

    # ensure should run the (mocked) creation path without error
    with patch("xde.core.project.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        rc = ensure_payload_project(quiet=True)
        assert rc == 0
        # We expect it tried to create (not the idempotent early return)
        assert mock_run.called
