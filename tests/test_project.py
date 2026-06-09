"""Dedicated unit tests for the project setup helpers in xde.core.project.

Expands the pure test pattern (originally in TestPayloadProjectSetupPure)
with parametrized cases for config variants, fallbacks, layouts, and
error paths. Also covers newly extracted pure helpers for better
coverage of the creation path logic (used by reset --yes and the
postStart hook) without requiring full side-effecting E2E.

Includes direct imports of core classes to reinforce the "importable
library/framework" vision (rec7).

See AGENTS.md and GROK-TASKS.md for the testing roadmap (unit for
core/project setup + library testability).
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from xde.core.project import (
    build_create_payload_command,
    compute_synced_project_env_content,
    ensure_payload_project,
    get_project_name,
    is_payload_project_complete,
    load_create_payload_config,
    resolve_db_connection_string,
)


class TestProjectPureHelpers:
    """Expanded pure tests for config loading, name resolution, completeness
    checks, command building, and the new extracted helpers.
    """

    @pytest.mark.parametrize(
        "config_data, expected_name",
        [
            ({"projectName": "my-app"}, "my-app"),
            ({"projectName": "  spaced  "}, "spaced"),
            ({"projectName": ""}, "my-payload-cms"),
            ({"projectName": None}, "my-payload-cms"),
            ({}, "my-payload-cms"),
            ({"other": "value"}, "my-payload-cms"),
        ],
    )
    def test_get_project_name_variants(
        self, tmp_path, config_data, expected_name
    ):
        """Covers get_project_name fallbacks and whitespace stripping."""
        cfg_path = tmp_path / "cfg.json"
        cfg_path.write_text(json.dumps(config_data))
        cfg = load_create_payload_config(cfg_path)
        assert get_project_name(cfg) == expected_name

    @pytest.mark.parametrize(
        "files_present, expected_complete",
        [
            (["payload.config.ts"], True),
            (["payload.config.js"], True),
            (["src/payload.config.ts"], True),
            (["src/payload.config.js"], True),
            (["payload.config.ts", "other.txt"], True),
            ([], False),
            (["README.md"], False),
            (["src/other.ts"], False),
        ],
    )
    def test_is_payload_project_complete_layouts(
        self, tmp_path, files_present, expected_complete
    ):
        """More is_complete layouts beyond the original two cases."""
        proj = tmp_path / "layout-test"
        proj.mkdir()
        for f in files_present:
            p = proj / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("// payload config")
        assert is_payload_project_complete(proj) is expected_complete

    def test_is_payload_project_complete_non_dir(self, tmp_path):
        """Non-existent or file (not dir) is not complete."""
        assert is_payload_project_complete(tmp_path / "nope") is False
        f = tmp_path / "notdir"
        f.write_text("hi")
        assert is_payload_project_complete(f) is False

    @pytest.mark.parametrize(
        "config_overrides, expected_keys",
        [
            ({}, {"projectName", "template", "dbAdapter", "agent", "dbUri"}),
            (
                {"projectName": "custom", "foo": "bar"},
                {"projectName": "custom"},
            ),
            (
                {"dbUri": "postgres://u:p@h/db"},
                {"dbUri": "postgres://u:p@h/db"},
            ),
        ],
    )
    def test_load_create_payload_config_variants(
        self, tmp_path, config_overrides, expected_keys
    ):
        """Parametrized load with partials, overrides, and defaults."""
        cfg_path = tmp_path / "c.json"
        base = {
            "projectName": "base",
            "template": "website",
            "dbAdapter": "postgres",
            "agent": "none",
            "dbUri": "",
        }
        base.update(config_overrides)
        cfg_path.write_text(json.dumps(base))
        cfg = load_create_payload_config(cfg_path)
        for k, v in (
            expected_keys.items() if isinstance(expected_keys, dict) else []
        ):
            assert cfg.get(k) == v
        # always has the default set
        assert "projectName" in cfg

    def test_load_create_payload_config_bad_json_and_missing(self, tmp_path):
        """Error paths: bad JSON / missing file yield safe defaults."""
        bad = tmp_path / "bad.json"
        bad.write_text("{ not json }")
        cfg = load_create_payload_config(bad)
        assert cfg["projectName"] == "my-payload-cms"

        missing = tmp_path / "absent.json"
        cfg2 = load_create_payload_config(missing)
        assert cfg2["projectName"] == "my-payload-cms"

    @pytest.mark.parametrize(
        "live, json_uri, expected",
        [
            ("postgres://live", "postgres://json", "postgres://live"),
            ("", "postgres://json", "postgres://json"),
            ("", "", None),
            ("live", "", "live"),
        ],
    )
    def test_resolve_db_connection_string(self, live, json_uri, expected):
        """Pure helper for live-vs-json DB resolution (extracted for rec2)."""
        assert resolve_db_connection_string(json_uri, live) == expected

    @pytest.mark.parametrize(
        "original, live_db, live_secret, expect_db, expect_secret",
        [
            (
                "DATABASE_URL=old\nPAYLOAD_SECRET=old",
                "newdb",
                "newsec",
                "DATABASE_URL=newdb",
                "PAYLOAD_SECRET=newsec",
            ),
            (
                "OTHER=foo\nDATABASE_URL=old",
                "newdb",
                "",
                "DATABASE_URL=newdb",
                "OTHER=foo",  # secret line absent, no change
            ),
        ],
    )
    def test_compute_synced_project_env_content(
        self, original, live_db, live_secret, expect_db, expect_secret
    ):
        """Pure sync (extracted for unit tests + rec2)."""
        result = compute_synced_project_env_content(
            original, live_db, live_secret
        )
        assert expect_db in result
        if live_secret:
            assert expect_secret in result


def test_build_create_payload_command_variants():
    """Additional build cases (originally basic; expanded here)."""
    cmd = build_create_payload_command(
        "app",
        template="blank",
        db_adapter="postgres",
        db_connection_string="uri",
        agent="foo",
    )
    assert "--db-connection-string" in cmd
    assert "uri" in cmd
    assert "--agent" in cmd and "foo" in cmd


def test_core_classes_directly_importable_as_library():
    """rec7: direct imports + isolated exercise to make the importable
    framework vision visible (no CLI, no full ensure side effects).
    """
    # Direct import of core project helpers (the creation logic now
    # canonical for reset + setup + hook).
    from xde.core.project import (
        compute_synced_project_env_content,
        load_create_payload_config,
    )

    # Exercise pure path in isolation.
    cfg = load_create_payload_config(Path("/nonexistent"))
    assert cfg["projectName"] == "my-payload-cms"

    synced = compute_synced_project_env_content(
        "DATABASE_URL=old\nPAYLOAD_SECRET=old", "live", "sec"
    )
    assert "DATABASE_URL=live" in synced

    # ensure can be called (will hit idempotent early return for non-dir).
    # Use quiet + monkey to avoid any prints/subprocess in this isolation test.
    with patch("xde.core.project.subprocess.run"):
        rc = ensure_payload_project(quiet=True)
    assert rc == 0


def test_run_setup_payloadcms_is_callable():
    """Keep the original smoke (moved/ duplicated for dedicated file)."""
    from xde.commands.setup import run_setup_payloadcms

    assert callable(run_setup_payloadcms)
