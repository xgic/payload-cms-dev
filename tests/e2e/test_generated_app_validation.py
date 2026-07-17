"""Placeholder E2E for generated Payload app validation after XGIC CLI commands.

Long-term: after ``xgic payload reset --yes`` + ``xgic payload dev``, assert
HTTP reachability (and later Playwright) for the generated app.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(
    reason=(
        "Long-term E2E skeleton. Requires reliable orchestration of "
        "'xgic payload reset --yes; xgic payload dev' + generated app listening."
    )
)
def test_generated_app_placeholder() -> None:
    assert False, "not implemented"
