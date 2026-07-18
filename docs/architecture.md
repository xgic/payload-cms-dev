# Architecture Overview

Mental model for humans and AI agents working on this **template**.

Multi-repo standards: https://github.com/xgic/ai  
CLI architecture: [ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md)

## High-level layers

1. **Host machine**
   - Docker Desktop / Engine, VS Code, Dev Containers extension.
   - Optional host install of modular XGIC CLI packages from **PyPI** (prefer working inside the container).

2. **Dev Container** (primary development environment)
   - Service defined in `.devcontainer/docker-compose.yml`.
   - Multi-stage `.devcontainer/Dockerfile` installs Node, tooling, and modular XGIC CLI into a Python venv.
   - Workspace bind-mounted; Payload project generated under the workspace when setup runs.
   - Database services (Postgres / Mongo) as compose profiles when needed.

3. **Modular XGIC CLI** (not implemented in this repo)
   - Console entry: `xgic`
   - Core framework: [xgic/cli](https://github.com/xgic/cli) (`xgic.cli`)
   - Docker Compose lifecycle: [xgic/dev-cli](https://github.com/xgic/dev-cli) (`xgic.cli.dev`)
   - Payload CMS product commands: [xgic/payload-cms-cli](https://github.com/xgic/payload-cms-cli) (`xgic.cli.payload`)

4. **Thin template scripts**
   - `.devcontainer/scripts/init-env.sh` — host-side env bootstrap
   - `.devcontainer/scripts/setup-payload.sh` — thin `exec xgic payload setup`
   - `.devcontainer/scripts/devcontainer-tests.sh` — environment smoke checks

## What this repo owns

| Asset | Role |
|-------|------|
| `.devcontainer/*` | Image, compose, Dev Container config |
| `create-payload-config.json` (+ schema) | Template config / IntelliSense |
| Thin bash shims | Delegate to `xgic` |
| Consumer `pyproject.toml` | PyPI pins for modular CLI + smoke tests |
| Docs / CI | Template quality gates |

## What this repo does **not** own

- CLI command implementations or libraries under `src/xde/` (removed at B5 cutover)
- A long-term `xde` entrypoint or alias
- Unit-test ownership for DockerComposeController / payload command logic (lives in modular packages)

## Agent tip

At the start of a non-trivial task, state whether you are changing:

1. **Template infrastructure** (Dockerfile, compose, scripts, CI) — work here, or  
2. **CLI behavior** — open a PR in the appropriate modular package repo instead.

Command map: [AGENTS.md](../AGENTS.md).
