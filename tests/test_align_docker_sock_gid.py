"""Unit tests for Docker engine socket GID alignment."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / ".devcontainer"
    / "scripts"
    / "align_docker_sock_gid.py"
)


def _load():
    spec = importlib.util.spec_from_file_location(
        "align_docker_sock_gid", SCRIPT
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_plan_groupmod_when_image_gid_differs() -> None:
    mod = _load()
    plan = mod.plan_align(
        990,
        docker_gid=994,
        gid_owners={994: "docker", 1000: "node"},
    )
    assert plan.reason == "groupmod-docker"
    assert plan.groupmod_docker_to == 990
    assert plan.add_user_to_groups == ("docker",)


def test_plan_already_matched_still_ensures_membership() -> None:
    mod = _load()
    plan = mod.plan_align(
        990,
        docker_gid=990,
        gid_owners={990: "docker"},
    )
    assert plan.reason == "already-matched"
    assert plan.groupmod_docker_to is None
    assert plan.add_user_to_groups == ("docker",)


def test_plan_joins_existing_group_that_owns_gid() -> None:
    mod = _load()
    plan = mod.plan_align(
        990,
        docker_gid=994,
        gid_owners={990: "staff", 994: "docker"},
    )
    assert plan.reason == "join-existing-gid-group"
    assert plan.groupmod_docker_to is None
    assert plan.add_user_to_groups == ("staff",)


def test_plan_skips_root_owned_or_missing_socket() -> None:
    mod = _load()
    missing = mod.plan_align(
        None, docker_gid=994, gid_owners={994: "docker"}
    )
    root = mod.plan_align(0, docker_gid=994, gid_owners={994: "docker"})
    assert missing.reason == "no-group-socket"
    assert root.reason == "no-group-socket"
    assert missing.groupmod_docker_to is None
    assert root.groupmod_docker_to is None
