# Architecture Overview

Mental model for humans and AI agents working on this **producer**.

Multi-repo standards: https://github.com/xgic/ai  
CLI architecture: [ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md)

## High-level layers

1. **Host machine**
   - Docker Desktop / Engine, VS Code, Dev Containers extension.
   - Optional host install of modular XGIC CLI packages from **PyPI** (prefer working inside the container).

2. **Dev Container** (primary development environment)
   - Service defined in `.devcontainer/docker-compose.yml` (Docker Compose–first; see [consumer contract](#consumer-contract-docker-compose-first)).
   - Multi-stage `.devcontainer/Dockerfile` installs Node, tooling, and modular XGIC CLI into a Python venv.
   - Workspace bind-mounted; Payload project generated under the workspace when setup runs.
   - Database services (Postgres / Mongo) as Docker Compose profiles when needed.

3. **Modular XGIC CLI** (not implemented in this repo)
   - Console entry: `xgic`
   - Core framework: [xgic/cli](https://github.com/xgic/cli) (`xgic.cli`)
   - Docker Compose lifecycle: [xgic/dev-cli](https://github.com/xgic/dev-cli) (`xgic.cli.dev`)
   - Payload CMS product commands: [xgic/payload-cms-cli](https://github.com/xgic/payload-cms-cli) (`xgic.cli.payload`)

4. **Optional scripts + explicit CLI**
   - Prefer **`xgic payload env` / `setup` / `dev`** from the modular CLI (no Dev Container host lifecycle hooks)
   - `.devcontainer/scripts/*` may remain as thin helpers for tests or migration; not required on container start
   - `.devcontainer/scripts/devcontainer-tests.sh` — environment smoke checks

## Consumer contract (Docker Compose–first)

This producer is the **source of truth** for how application templates and
downstream apps must reopen the Dev Container. The thin template
([payload-cms](https://github.com/xgic/payload-cms)) implements the same
contract ([payload-cms#10](https://github.com/xgic/payload-cms/issues/10) /
[PR #11](https://github.com/xgic/payload-cms/pull/11)).

### Supported shape

| Requirement | Detail |
|-------------|--------|
| Attach path | `dockerComposeFile` + `service` in `devcontainer.json` |
| Image pin | On the **Docker Compose** primary service (`image: ghcr.io/xgic/payload-cms-dev:<semver>`), not a standalone `image:` in `devcontainer.json` |
| Stable project | Top-level Docker Compose `name:` (default `xgic-payload-cms-dev`) |
| CLI alignment | `XGIC_COMPOSE_PROJECT` / `XGIC_COMPOSE_FILE` / `XGIC_PRIMARY_SERVICE` on the primary service; keep `composeProjectName` in `create-payload-config.json` in sync |
| Database | Same Docker Compose project as the IDE attach (e.g. Postgres via `runServices` / `depends_on` health in the template) |

This repository’s `.devcontainer/` is the **exemplar** (local Dockerfile build
for producer work). Consumers pull the published GHCR image on the same service
key pattern.

### Anti-pattern: standalone `image:` reopen

Do **not** reopen with only `"image": "ghcr.io/xgic/payload-cms-dev:…"` in
`devcontainer.json`. That path:

- Assigns non-deterministic container names (Docker’s default `adjective_noun` style)
- Leaves the database **outside** the IDE Docker Compose project
- Diverges from CLI expectations (`xgic up`, `composeProjectName`, `XGIC_COMPOSE_PROJECT`)

If a workspace is still on that anti-pattern, run **Dev Containers: Rebuild
Container** once after switching to Docker Compose.

### Bind-mount performance

Bind-mounted workspaces can be slow for large Node module graphs on any Docker
host. Prefer a native Linux filesystem for the workspace long term; optional
named volumes over `node_modules` / `.next` are an explicit documented bridge.
Details: [dev-performance.md](dev-performance.md).

### Related issues

| Topic | Link |
|-------|------|
| Producer docs (this contract) | [#50](https://github.com/xgic/payload-cms-dev/issues/50) |
| Template Compose-first reopen | [payload-cms#10](https://github.com/xgic/payload-cms/issues/10) / [PR #11](https://github.com/xgic/payload-cms/pull/11) |
| CLI env / credential sync | [payload-cms-cli#26](https://github.com/xgic/payload-cms-cli/issues/26) |
| Host-conditional Git DX | [#49](https://github.com/xgic/payload-cms-dev/issues/49) |

## What this repo owns

| Asset | Role |
|-------|------|
| `.devcontainer/*` | Image, Docker Compose, Dev Container config (consumer-contract exemplar) |
| `create-payload-config.json` (+ schema) | Producer config / IntelliSense |
| Git DX | Compose start chowns `ssh-home` + `configure-git-dx.sh --quiet` (HTTPS prefer by default; no `devcontainer.json` hooks) |
| Consumer `pyproject.toml` | PyPI pins for modular CLI + smoke tests |
| Docs / CI | Producer quality gates + consumer-contract documentation |

## What this repo does **not** own

- CLI command implementations or libraries under `src/xde/` (removed at B5 cutover)
- A long-term `xde` entrypoint or alias
- Unit-test ownership for DockerComposeController / payload command logic (lives in modular packages)

## Agent tip

At the start of a non-trivial task, state whether you are changing:

1. **Producer infrastructure** (Dockerfile, Docker Compose, scripts, CI, consumer-contract docs) — work here, or  
2. **CLI behavior** — open a PR in the appropriate modular package repo instead.

Command map: [AGENTS.md](../AGENTS.md).
