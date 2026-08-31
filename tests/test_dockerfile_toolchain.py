"""Toolchain pins encoded in the producer Dockerfile."""

from pathlib import Path

DOCKERFILE = (
    Path(__file__).resolve().parents[1] / ".devcontainer" / "Dockerfile"
)


def test_pnpm_is_pinned_via_corepack_prepare() -> None:
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert "corepack prepare pnpm@10.34.5 --activate" in text
    assert "corepack use pnpm@10" not in text


def test_next_telemetry_disabled() -> None:
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert "NEXT_TELEMETRY_DISABLED=1" in text
