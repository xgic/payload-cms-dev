# Testing Strategy for XGIC Payload CMS Dev Containers

## Current State

- **Unit test coverage focus**: Core `src/xde/core/` (EnvironmentContext, DockerComposeController) and command logic via `pytest` (direct).
  - Legacy `reset-project.py` and its fidelity tests have been removed (migration complete).
  - Remaining Python tests emphasize the active xde implementation (reset, env, docker controller, etc.).
- **Integration/smoke testing**: `devcontainer-tests.sh` (version + connectivity checks) and manual `xde check` / `xde dev` / `xde reset --dry-run` flows inside the container.
- **Python code under test focus**: The live `src/xde/` modules (highest value for day-to-day reliability and agent productivity).

> **Note on Python test tooling**: `pytest`, `pytest-cov`, and `pytest-mock` are installed on-demand the first time you run the test commands (see TESTING.md "Running Tests" section). They are not in the base image to keep it lean.

## Testing Philosophy

This is a **Dev Container + DX tooling** repository, not a traditional application.

**Priorities (in order):**

1. **Reliability of destructive operations** (now `xde reset` + the DockerComposeController volume/DB paths)
2. **Correctness of credential and config handling** (env regeneration, create-payload-config)
3. **Schema validation** (for excellent VS Code DX via the single source of truth)
4. **Smoke testing** of the container environment (`xde check`, `devcontainer-tests.sh`)
5. High line coverage on shell scripts (low priority — hard to test meaningfully; rely on idempotency + manual runs inside the container)

## Recommended Coverage Targets (for future work)

| Component                    | Target Coverage | Rationale |
|-----------------------------|------------------|---------|
| `src/xde/core/` (controller + env) | High (focus area) | The live orchestration and credential logic that reset, dev, etc. depend on |
| Reset + DB/volume paths     | High            | Highest-risk user-facing destructive operation |
| Config loading + schema     | High            | Small and critical for the whole template |
| Shell scripts (init/setup)  | Not measured    | Use `devcontainer-tests.sh` + `xde reset --dry-run` / manual verification inside the container |
| Overall (active Python)     | **≥ 70%**       | Target for the xde implementation (legacy reset-project artifacts removed) |

## Running Tests (Current)

```bash
# Inside the dev container (recommended primary environment)
# Ensure dev extras if needed: python -m pip install -e '.[dev]'
PYTHONPATH=src python -m pytest tests/ -q
PYTHONPATH=src python -m pytest tests/ --cov=src/xde --cov-report=term-missing
```

Direct `pytest` usage (no legacy shims).

Integration/smoke behavior is exercised via:
- ` .devcontainer/scripts/devcontainer-tests.sh` (Node/pnpm + basic connectivity/version checks at different container lifecycle points)
- Manual `xde check`, `xde env`, `xde reset --dry-run`, `xde dev` (targeted) flows inside the running dev container.

**AI assistants**: See (in priority order):
1. [AGENTS.md](AGENTS.md) — testing philosophy + "good testability of the core logic" as a foundation.
2. [GROK-TASKS.md](GROK-TASKS.md) — Testing & Automation Roadmap (unit for core xde logic → integration → E2E including generated Payload apps).
3. [docs/grok-playbooks.md](docs/grok-playbooks.md)
4. [docs/architecture.md](docs/architecture.md)

These contain the current priorities (focus on `src/xde/core/` + commands that own destructive flows and project scaffolding).

## Current State (as of post-0.1.0 work)

- Focused unit tests on active `src/xde/` (EnvironmentContext, DockerComposeController with services= / rm_service / direct volume, env regeneration, dev launch paths, and the new `core/project.py` + `commands/setup.py` for `xde setup payloadcms`).
- 33 tests (all passing in current runs): strong pure-function + controller coverage + dedicated tests for the project ensure logic used by reset + the hook.
- Overall line coverage on `src/xde/` ~53% (higher on core abstractions; lower on thin CLI dispatch and some side-effect paths in project ensure / command run_ functions — see verification run for exact term-missing report).
- No more legacy `reset-project.py` fidelity tests or old macro harness (correctly removed).

## Adding New Tests

- Place unit tests in `tests/`.
- Use `pytest` + `pytest-mock` (or monkeypatch) for filesystem/subprocess/config.
- Prefer testing pure functions (see the excellent `TestPayloadProjectSetupPure` pattern for `load_*`, `is_complete`, `build_create...` in `core/project.py` and the expanded coverage in `tests/test_project.py`).
- Side-effect heavy paths (actual `pnpx create-payload-app`, live secret sync) are intentionally best-effort and covered via the idempotent devcontainer hook + manual `xde reset --yes ; xde dev` flows inside the container.
- Integration: see the lightweight skeleton under `tests/integration/` (temp config fixtures + example combined flows; can grow to drive real targeted `up(services=...)` + project creation).
- E2E (long-term per roadmap): after `xde dev` + project creation (or `reset --yes`), validate the generated Payload app. Initial skeleton in `tests/e2e/` (skipped placeholder describing HTTP checks on :3000 + admin reachability; Playwright for browser flows later).

## CI / Gates

Python tests + coverage run via GitHub workflows on push/PR. Ruff (format + check, 80-col for code files) is enforced. Any commit touching code must pass ruff + all relevant tests (per AGENTS).

## Future Improvements (aligned with roadmap)

- Dramatically increase unit coverage for remaining core paths (especially project ensure side effects, full reset + setup integration, config edge cases).
- Add integration tests exercising real Docker Compose + complete dev lifecycle (targeted up, project creation, dev server).
- E2E that create a full generated Payload app (via `xde setup payloadcms` or reset) and validate it (including browser-level with Playwright where valuable).
- Property-based / golden-file tests for config + generated `.env`.
- Keep the library-friendly design: core classes (`EnvironmentContext`, `DockerComposeController`, `ensure_payload_project`, etc.) should remain easy to import and test in isolation for use by external tools.

---

**Goal**: High confidence in the most dangerous parts of the tooling (reset, credential handling, project scaffolding) and the core abstractions that agents rely on, while progressively moving toward the published unit → integration → E2E (generated apps) roadmap. The recent addition of well-tested pure logic in `core/project.py` (used by both `xde setup payloadcms` and reset) is a concrete step in the right direction.
