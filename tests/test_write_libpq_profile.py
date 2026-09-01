"""libpq profile is generated from create-payload-config.json, not hardcoded."""

from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from xgic.cli.payload.config import get_db_config

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT / ".devcontainer" / "scripts" / "write_libpq_profile.py"
)


def _load():
    spec = spec_from_file_location("write_libpq_profile", SCRIPT)
    assert spec and spec.loader
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_exports_follow_config_dbname(tmp_path: Path) -> None:
    cfg = tmp_path / "create-payload-config.json"
    cfg.write_text(
        json.dumps({"dbName": "site_db", "dbUser": "site_user"}),
        encoding="utf-8",
    )
    assert get_db_config(cfg) == ("site_db", "site_user")
    text = _load().libpq_exports(cfg)
    assert text is not None
    assert "export PGDATABASE=site_db\n" in text
    assert "export PGUSER=site_user\n" in text
    assert "payload_db" not in text
    assert "PGUSER=payload\n" not in text


def test_omitted_keys_use_schema_defaults(tmp_path: Path) -> None:
    cfg = tmp_path / "create-payload-config.json"
    cfg.write_text("{}", encoding="utf-8")
    db_name, db_user = get_db_config(cfg)
    text = _load().libpq_exports(cfg)
    assert text is not None
    assert f"export PGDATABASE={db_name}\n" in text
    assert f"export PGUSER={db_user}\n" in text


def test_missing_config_is_noop(tmp_path: Path) -> None:
    assert _load().libpq_exports(tmp_path / "missing.json") is None


def test_writes_output_path(tmp_path: Path) -> None:
    cfg = tmp_path / "create-payload-config.json"
    cfg.write_text(
        json.dumps({"dbName": "custom_db", "dbUser": "custom_user"}),
        encoding="utf-8",
    )
    out = tmp_path / "profile.d" / "xgic-libpq.sh"
    mod = _load()
    assert mod.main(["--config", str(cfg), "--output", str(out)]) == 0
    written = out.read_text(encoding="utf-8")
    assert "PGDATABASE=custom_db" in written
    assert "payload_db" not in written
