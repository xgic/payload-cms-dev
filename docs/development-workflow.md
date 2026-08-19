# Development Workflow

How we work on this **template** repository. Environment operations use the modular **XGIC CLI** (`xgic`). CLI implementation changes belong in the modular package repos, not here.

These guidelines apply to both human contributors and AI-assisted development (Grok Build).

## Core principles

- **Reliability over speed**: Changes that land on `main` must be reliable.
- **Agent productivity is first-class**: Prefer documented `xgic` commands and clear AGENTS guidance.
- **Consumer-only template**: Do not reintroduce an in-tree CLI package.
- **Positive, constructive tone**: Focus on excellent experiences; reference the past only to prevent regression.

## Commit discipline

- Atomic, logical units of change; Conventional Commits.
- Every code commit should pass relevant lint + tests and update docs when user-visible behavior changes.
- Clean published history on protected branches (rebase/squash as appropriate before merge).

## Testing requirements

Before committing template/code changes:

```bash
uv pip install -e ".[dev]"
uv run pytest -q
# shell / workflow gates are enforced in CI; run shellcheck/shfmt locally when touching scripts
```

Manual environment smoke inside the Dev Container:

```bash
xgic check
xgic payload env
xgic payload reset --dry-run
```

Details: [TESTING.md](../TESTING.md).

## Docker and Docker Compose

- Template compose: `.devcontainer/docker-compose.yml`
- Image build: `.devcontainer/Dockerfile`
- Product-agnostic Docker Compose control lives in **xgic/dev-cli** (`DockerComposeController`); open changes there if orchestration behavior must change.

## Working with AI assistants

- Follow [AGENTS.md](../AGENTS.md).
- Session startup: `xgic --help`, `xgic check`, `xgic payload env`.
- Human UI review before merge to `main`.
