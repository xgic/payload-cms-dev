"""Unit tests for e2e reachability helpers (no live Payload server)."""

from __future__ import annotations

from tests.e2e.conftest import url_reachable, wait_reachable


def test_url_reachable_closed_port_is_false() -> None:
    assert url_reachable("http://127.0.0.1:1", timeout=0.2) is False


def test_wait_reachable_closed_port_is_false() -> None:
    assert (
        wait_reachable(
            "http://127.0.0.1:1",
            attempts=2,
            timeout=0.2,
            pause=0.0,
        )
        is False
    )
