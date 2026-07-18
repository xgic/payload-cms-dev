# xde Command Reference (HISTORICAL)

> **Archived.** Supported `xde` was retired at B5 hard cutover. Living brand: **XGIC CLI** (`xgic`).  
> Current command map: [AGENTS.md](../AGENTS.md). Modular packages: [xgic/cli](https://github.com/xgic/cli), [xgic/dev-cli](https://github.com/xgic/dev-cli), [xgic/payload-cms-cli](https://github.com/xgic/payload-cms-cli).  
> Architecture: [ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md).

This document is retained only as a historical snapshot of the pre-cutover `xde` surface.

## Design Principles

- Small surface area
- One obvious way to do the common thing
- `--dry-run` and `--yes` where it matters
- Excellent default behavior + escape hatches
- Output that is useful for both humans (Rich) and agents (eventual `--json`)

## Current / Planned Commands

### `xde` (bare)

Shows short, high-signal help (level 1). This is what an agent should see first.

### `xde dev`

**The most important command.**

Intended behavior:
- Ensure services are running (`up` if needed).
- Perform database readiness check with friendly guidance.
- Change into the generated Payload project directory.
- Execute `pnpm dev`.

This should be the command a human or agent runs when they want to "just start working."

### `xde up`

Start all services in detached mode.

Flags (future):
- `--build`

### `xde down`

Stop services. Volumes are preserved by default.

### `xde reset`

Fast, targeted reset.

What it does (current design):
- Delete the generated Payload project folder.
- Reset only the Postgres volume (data destroyed).
- Credentials in `.env` are **intentionally left alone** (this is a deliberate, hard-won design decision).

Important flags:
- `--yes` — Skip confirmation
- `--rotate-credentials` — Also rotate DB password + PAYLOAD_SECRET (rarely needed)
- `--dry-run` — Show exactly what would happen

This is one of the highest-value commands for both humans and agents.

### `xde check`

Diagnostic command.

Should report on:
- Are the expected containers running?
- Can we reach PostgreSQL?
- Is the generated Payload project in a good state?
- Any obvious configuration issues?

Extremely useful for agents to call at the start of a session or when something feels wrong.

### `xde build [--no-cache]`

Build images. The `--no-cache` flag replaces the old proliferation of `docker-build-only-nocache` style targets.

### `xde logs`

Follow logs.

### `xde shell`

Drop into an interactive shell inside the main service container.

### `xde env`

Inspect and manage the generated `.env` file and related state.

Subcommands (planned):
- `xde env show`
- `xde env regenerate`

### `xde clean`

Higher danger level than `reset`.

Intended for when you want to nuke almost everything (volumes + `.env`).

Must have very strong warnings and confirmation.

### Future / Lower Priority

- `xde schema generate`
- `xde config` (read values from `create-payload-config.json`)
- `xde exec` (thin wrapper around docker compose exec)

**Deliberately not in scope** (and unlikely to be added):
- `xde test`, `xde lint`, `xde validate`, or similar "run all the things" commands for code quality.

`xde` is intentionally scoped to dev container orchestration and the generated Payload project lifecycle. Code formatting, linting (`ruff`), and testing (`pytest`) use the standard tools directly. This keeps the command surface small and predictable (see AGENTS.md "Command surface bloat" pitfall and the v1 surface proposal) and makes the actual quality tooling transparent to both humans and agents. `xde check` is strictly for environment health (services, DB, project folder).

---

## Agent Usage Patterns

**Exploration / Orientation**
```bash
xde --help
xde check
xde env
```

**Normal development loop**
```bash
xde dev
# work...
xde reset --dry-run
# (explain to human)
xde reset --yes
xde dev
```

**When you suspect environment corruption**
```bash
xde check
xde reset --dry-run
```

Always prefer `xde` commands over raw `docker compose` (unless performing advanced low-level debugging).

**Grok Tip**: When a command is not yet fully implemented, still document what the *ideal* behavior should be in this file. This helps future sessions stay aligned on the vision.

---

**Last updated**: 2026

This document should be kept in sync with actual command implementations in `src/xde/cli.py`.