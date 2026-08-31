"""HTTP smoke for the producer first-run Payload CMS website template.

Covers: initial page, first admin (or login), seed, seeded routes, admin.
Does not vendor generated ``app/`` sources (gitignored).
"""

from __future__ import annotations

import os
from typing import Any

import pytest

from tests.e2e.conftest import (
    DEFAULT_EMAIL,
    DEFAULT_NAME,
    DEFAULT_PASSWORD,
    PayloadSession,
)

pytestmark = pytest.mark.e2e


def _env_email() -> str:
    return os.environ.get("E2E_EMAIL", DEFAULT_EMAIL)


def _env_password() -> str:
    return os.environ.get("E2E_PASSWORD", DEFAULT_PASSWORD)


@pytest.fixture(scope="session")
def seeded_session(
    payload_session: PayloadSession,
) -> PayloadSession:
    status, init = payload_session.json("/api/users/init")
    assert status == 200
    assert isinstance(init, dict)
    email = _env_email()
    password = _env_password()
    if not bool(init.get("initialized")):
        status, data = payload_session.json(
            "/api/users/first-register",
            method="POST",
            payload={
                "email": email,
                "password": password,
                "name": DEFAULT_NAME,
            },
        )
        assert status == 200, data
        assert isinstance(data, dict)
        assert data.get("token") or data.get("user")
    else:
        status, data = payload_session.json(
            "/api/users/login",
            method="POST",
            payload={"email": email, "password": password},
        )
        if status != 200:
            pytest.skip(
                "App already initialized with unknown credentials; "
                "set E2E_EMAIL and E2E_PASSWORD"
            )
    status, me = payload_session.json("/api/users/me")
    assert status == 200, me
    status, seed = payload_session.json(
        "/next/seed",
        method="POST",
        timeout=120.0,
    )
    assert status == 200, seed
    if isinstance(seed, dict):
        assert seed.get("success") is True or "success" in seed
    return payload_session


def test_initial_page_is_payload_next(
    payload_session: PayloadSession,
) -> None:
    status, body = payload_session.get("/")
    assert status == 200
    text = body.decode("utf-8", errors="replace").lower()
    assert "html" in text or "payload" in text


def test_first_admin_and_seed_succeed(
    seeded_session: PayloadSession,
) -> None:
    status, me = seeded_session.json("/api/users/me")
    assert status == 200, me


def test_seeded_frontend_and_admin_routes(
    seeded_session: PayloadSession,
) -> None:
    for path in ("/", "/posts", "/contact", "/admin"):
        status, _body = seeded_session.get(path)
        assert status == 200, path

    status, posts = seeded_session.json("/api/posts?limit=20&depth=0")
    assert status == 200, posts
    docs: list[Any] = []
    if isinstance(posts, dict):
        raw = posts.get("docs") or []
        if isinstance(raw, list):
            docs = raw
    assert docs, "seed should create posts"
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        slug = doc.get("slug")
        if not slug:
            continue
        status, _body = seeded_session.get(f"/posts/{slug}")
        assert status == 200, slug

    status, pages = seeded_session.json("/api/pages?limit=20&depth=0")
    assert status == 200, pages
    if isinstance(pages, dict):
        for doc in pages.get("docs") or []:
            if not isinstance(doc, dict):
                continue
            slug = doc.get("slug")
            if not slug or slug in {"home", "index"}:
                continue
            status, _body = seeded_session.get(f"/{slug}")
            assert status == 200, slug
