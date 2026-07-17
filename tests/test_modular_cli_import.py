"""Smoke: modular XGIC CLI packages import after cutover."""

from __future__ import annotations


def test_core_and_payload_importable() -> None:
    from xgic.cli import __version__
    from xgic.cli.payload import ensure_payload_project

    assert __version__
    assert callable(ensure_payload_project)


def test_dev_controller_importable() -> None:
    from xgic.cli.dev import DockerComposeController

    assert DockerComposeController is not None
