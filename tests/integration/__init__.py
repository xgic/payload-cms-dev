"""Lightweight integration test skeleton for xde.

Intended for flows that combine multiple components (e.g. targeted
DockerComposeController.up(services=...) + project ensure / creation).

Fixtures here provide temp configs and can be extended with real or
mocked compose profiles later (see rec5 in test coverage plan).

See TESTING.md for how this fits the unit → integration → E2E roadmap.
"""

from __future__ import annotations
