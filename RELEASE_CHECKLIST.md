# XGIC Payload CMS Dev (`payload-cms-dev`) — Release Checklist

Checklist for shipping the **Dev Container image producer**. This repository installs modular **XGIC CLI** packages from PyPI ([ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md)) and publishes **`ghcr.io/xgic/payload-cms-dev`**. End-user template: [xgic/payload-cms](https://github.com/xgic/payload-cms).

## Session & environment health (every time)

Inside the Dev Container:

```bash
xgic --help
xgic check
xgic payload env
xgic payload reset --dry-run
```

- [ ] `xgic check` reports service/environment status as expected
- [ ] `xgic payload env` shows sensible configuration
- [ ] `xgic payload reset --dry-run` blast radius is accurate

## Code & automated gates

```bash
uv pip install -e ".[dev]"
uv run pytest -q
uv run xgic --version
uv run xgic payload --help
```

- [ ] CI **Lint**, **Test**, and **Release Validation** gates green on the PR
- [ ] No reintroduction of in-tree CLI / `xde` entrypoint
- [ ] `pyproject.toml` / Dockerfile pins still target intended PyPI versions
- [ ] Docs updated in the same change set when behavior changes (AGENTS, README, TESTING)

## Manual high-value flows

- [ ] `xgic payload setup` is idempotent when run explicitly
- [ ] Optional: `xgic payload reset --yes` then `xgic payload setup` / `xgic payload dev` for a clean project path (only after dry-run)
- [ ] Target DB adapter path for the release still works (Postgres default; Mongo if in scope)
- [ ] `create-payload-config.json` + schema still provide good editor IntelliSense

**Safety:** never run destructive `xgic payload reset --yes` or full clean without `--dry-run` first during validation.

## Documentation

- [ ] README XGIC CLI quick reference is current
- [ ] AGENTS.md command map is current
- [ ] CONTRIBUTING / TESTING match consumer model (no living `src/xde` instructions)
- [ ] Historical `xde` material is clearly archived, not presented as current

## GHCR image

- [ ] **Publish GHCR** workflow green on `main` and/or `v*` tag
- [ ] Image pull works: `docker pull ghcr.io/xgic/payload-cms-dev:latest` (or semver tag)
- [ ] End-user template [payload-cms](https://github.com/xgic/payload-cms) `devcontainer.json` pin updated when cutting a release tag

## Git hygiene

- [ ] Dedicated issue branch; Conventional Commits; required labels
- [ ] Human UI review before merge to `main`
- [ ] No committed secrets, generated apps, or `.env` files
