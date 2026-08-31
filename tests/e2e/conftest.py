"""E2E fixtures: skip unless a Payload CMS app is listening."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
from typing import Any

import pytest

DEFAULT_BASE = "http://127.0.0.1:3000"
DEFAULT_EMAIL = "e2e-admin@example.com"
DEFAULT_PASSWORD = "E2eTestPass1!"
DEFAULT_NAME = "E2E Admin"


def e2e_base_url() -> str:
    return os.environ.get("PAYLOAD_BASE_URL", DEFAULT_BASE).rstrip("/")


def e2e_require() -> bool:
    return os.environ.get("E2E_REQUIRE", "").lower() in {
        "1",
        "true",
        "yes",
    }


def url_reachable(url: str, timeout: float = 2.0) -> bool:
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


class PayloadSession:
    """Cookie-aware HTTP helper for the generated website template."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def open(
        self,
        path: str,
        *,
        data: bytes | None = None,
        method: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 120.0,
    ) -> tuple[int, bytes, str]:
        req = urllib.request.Request(
            self._url(path),
            data=data,
            method=method,
            headers=headers or {},
        )
        try:
            with self.opener.open(req, timeout=timeout) as resp:
                body = resp.read()
                ctype = resp.headers.get("Content-Type", "")
                return resp.status, body, ctype
        except urllib.error.HTTPError as e:
            body = e.read()
            ctype = e.headers.get("Content-Type", "") if e.headers else ""
            return e.code, body, ctype

    def get(self, path: str, timeout: float = 120.0) -> tuple[int, bytes]:
        status, body, _ = self.open(path, timeout=timeout)
        return status, body

    def json(
        self,
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, Any] | None = None,
        timeout: float = 120.0,
    ) -> tuple[int, Any]:
        headers = {"Accept": "application/json"}
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        status, body, ctype = self.open(
            path,
            data=data,
            method=method,
            headers=headers,
            timeout=timeout,
        )
        parsed: Any
        try:
            parsed = json.loads(body.decode("utf-8")) if body else None
        except json.JSONDecodeError:
            parsed = body.decode("utf-8", errors="replace")
        if "json" not in ctype.lower() and not isinstance(parsed, dict):
            return status, parsed
        return status, parsed


@pytest.fixture(scope="session")
def payload_session() -> PayloadSession:
    base = e2e_base_url()
    if url_reachable(base):
        return PayloadSession(base)
    if e2e_require():
        pytest.fail(
            f"E2E_REQUIRE is set but {base} is not reachable. "
            "Start: xgic payload setup && xgic payload dev"
        )
    pytest.skip(f"Payload CMS app not running at {base}")
