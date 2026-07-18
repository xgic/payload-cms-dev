# Testing Strategy for XGIC Payload CMS Dev Containers

## Current state (post B5 cutover)

This repository is a **Dev Container template / consumer** of modular **XGIC CLI** packages from PyPI. It does **not** ship an in-tree CLI library.

| Layer | Where tests live |
|-------|------------------|
| Template smoke / consumer imports | This repo (`tests/`, CI `Test` workflow) |
| CLI unit + integration tests | [xgic/cli](https://github.com/xgic/cli), [xgic/dev-cli](https://github.com/xgic/dev-cli), [xgic/payload-cms-cli](https://github.com/xgic/payload-cms-cli) |
| Container tooling smoke | `.devcontainer/scripts/devcontainer-tests.sh`, `Release Validation` workflow |

**Brand:** living docs use **XGIC CLI** / `xgic` only. Historical `xde` notes belong in archived docs, not this strategy.

## Testing philosophy

Priorities for **this** repository:

1. **Image and Docker Compose buildability** (Dockerfile, compose, init-env)
2. **Consumer install** from PyPI pins (`pyproject.toml` → `uv pip install -e ".[dev]"`)
3. **Entrypoint smoke** (`xgic --version`, `xgic payload --help`)
4. **Shell / workflow quality** (ShellCheck, actionlint, shfmt, yamllint)
5. **Manual environment flows** inside the Dev Container (`xgic check`, `xgic payload dev`, `xgic payload reset --dry-run`)

Destructive and orchestration logic is tested in the modular CLI packages, not re-owned here.

## Running tests

```bash
# Inside the Dev Container or a local uv env (Python 3.14+)
uv pip install -e ".[dev]"
uv run pytest -q
uv run xgic --version
uv run xgic payload --help
```

CI mirrors this (see `.github/workflows/test.yml`). Release validation builds the Dev Container image and smoke-tests tooling + XGIC CLI inside the container (see `.github/workflows/release-validation.yml`).

## Manual smoke (high value)

Inside the running Dev Container:

```bash
xgic --help
xgic check
xgic payload env
xgic payload reset --dry-run
# optional full flow
xgic payload setup
xgic payload dev
```

Always prefer `--dry-run` before destructive `xgic payload reset --yes`.

## Coverage expectations

| Component | Target | Notes |
|-----------|--------|-------|
| Template Python smoke (`tests/`) | Pass in CI | Import modular packages; no in-tree CLI coverage target |
| Modular CLI packages | Owned by those repos | Do not reimplement unit suites here |
| Shell scripts | ShellCheck + manual | `devcontainer-tests.sh` for environment smoke |

## Related

- [AGENTS.md](AGENTS.md) — command map for agents
- [docs/architecture.md](docs/architecture.md) — consumer architecture
- [python-package-release.md](https://github.com/xgic/ai/blob/main/docs/python-package-release.md) — PyPI install path
