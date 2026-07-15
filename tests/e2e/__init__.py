"""E2E harness skeleton for validating generated Payload apps (rec6).

Long-term goal (testing roadmap in AGENTS.md / docs): after `xde reset --yes; xde dev`
(or setup), validate the produced app (HTTP on :3000, admin
reachability; later full Playwright browser flows for the
Payload frontend/admin).

Start lightweight so it can grow without blocking unit/integration work.
"""

from __future__ import annotations
