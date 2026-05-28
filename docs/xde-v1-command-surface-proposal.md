# xde v1 Command Surface Proposal

**Date**: June 2026  
**Status**: Proposal for discussion and agreement  
**Goal**: Define the minimal, final command surface for `xde` v1 that is simple, powerful, and sufficient to eventually retire the Makefile.

---

## Executive Summary

The current direction of `xde` is already very good. This proposal recommends **locking a small, clean surface** now so that implementation can proceed with confidence and minimal future refactoring.

**Recommended v1 Surface** (10 top-level commands):

```bash
xde                    # Short, high-signal help
xde dev                # The primary daily command
xde up
xde down
xde reset              # Fast targeted reset (with strong safeguards)
xde check
xde build [--no-cache]
xde logs
xde shell
xde env                # Environment inspection + management
xde clean              # Full environment cleanup (high danger)
```

This surface covers ~85-90% of the *valuable* functionality that people actually use from the current Makefile, while being dramatically simpler.

**Key Recommendations**:
- Drop the `stage` subcommand entirely for v1 (already removed in current code).
- Use flags instead of many similar commands (`--no-cache`, `--yes`, `--dry-run`, `--rotate-credentials`).
- Keep `env` as a lightweight top-level command with future subcommands.
- Make `--dry-run` and clear next-step messaging a first-class design principle.

---

## Current State (What We Have Today)

From `src/xde/cli.py`:

| Command     | Status          | Notes |
|-------------|-----------------|-------|
| `dev`       | Stub            | Highest value command |
| `up`        | Partially real  | Uses DockerComposeController |
| `down`      | Partially real  | Uses DockerComposeController |
| `reset`     | Stub            | Critical command |
| `check`     | Stub            | Very high agent value |
| `build`     | Partially real  | Supports `--no-cache` |
| `logs`      | Stub            | - |
| `shell`     | Stub            | - |
| `env`       | Stub            | - |
| `clean`     | Stub            | High danger |

The `stage` subtree has already been removed — this is the correct direction.

---

## Proposed Final v1 Surface

### Top-Level Commands

| Command     | Purpose                                      | Key Flags                          | Replaces (Makefile) |
|-------------|----------------------------------------------|------------------------------------|---------------------|
| `dev`       | Smart "start working" experience             | (future: `--no-up`)                | `dev`, `dev-all` |
| `up`        | Start services                               | `--build`                          | `up` |
| `down`      | Stop services (volumes preserved)            | -                                  | `down` |
| `reset`     | Fast targeted reset (project + postgres)     | `--yes`, `--dry-run`, `--rotate-credentials` | `reset-project` |
| `check`     | Health diagnostics                           | `--json` (future)                  | `check-db`, `test-db`, parts of `ps` |
| `build`     | Build images                                 | `--no-cache`                       | All `docker-build-*` variants |
| `logs`      | Follow logs                                  | -                                  | `logs` |
| `shell`     | Interactive shell in main service            | -                                  | `shell`, `exec-shell` |
| `env`       | Inspect and manage environment               | `regenerate` (subcommand later)    | `env`, `env-regenerate`, `refresh-env` |
| `clean`     | Full environment cleanup (volumes + .env)    | `--yes`                            | `clean`, `reset` (the dangerous one) |

### Design Principles for This Surface

1. **Small surface area** — 10 top-level commands max for v1.
2. **One obvious way** — No aliases or duplicate paths.
3. **Flags over sub-variants** — `--no-cache`, `--yes`, `--dry-run`, `--rotate-credentials`.
4. **Safety by default** — Destructive commands require explicit confirmation or `--yes`.
5. **Agent friendly** — Predictable names, good `--help`, future `--json` support on diagnostic commands.
6. **Progressive disclosure** — `env` and `reset` can grow subcommands later without bloating the top level.

---

## What We Are Explicitly Dropping for v1

- **All `stage` commands** — Too much surface for v1. Can be re-introduced later as `xde stage ...` if real demand appears.
- Most build variants (`docker-build-only`, `docker-build-only-nocache`, etc.) → covered by `xde build [--no-cache]`.
- `prune` — Too dangerous and system-wide. Keep it out or put it under `xde clean --system-prune` (if we decide to support it).
- Most lint/validate targets (`lint-shell`, `validate-python`, `lint-makefile`, etc.) — These can remain in the Makefile during transition or become `xde validate` later.
- `exec` and `python` — Power-user commands. Can be added later as `xde exec` if needed.
- `init-env` and `create-payload` — These are mostly lifecycle hooks. `xde` can call into them, but they don't need to be direct user commands in v1.

---

## Rationale

### Why This Surface Is Efficient

- It covers the **daily development loop** extremely well (`dev`, `up`, `down`, `reset`, `check`).
- It gives agents a small, predictable vocabulary.
- It removes the biggest source of confusion from the old Makefile (many similar build targets, aliases, internal targets leaking into user space).
- It positions `reset` and `check` as first-class citizens (they are disproportionately valuable).

### Why Not More Commands?

Every additional top-level command increases cognitive load for both humans and agents. The goal is **"I only need to remember ~8-10 commands to be highly productive."**

### Why Not Fewer?

We still need distinct primitives for:
- Smart happy path (`dev`)
- Lifecycle control (`up`/`down`/`build`)
- The most common destructive operation (`reset`)
- Diagnostics (`check`)
- Visibility (`env`, `logs`, `shell`)

---

## Migration Mapping (High Level)

| Common Old Usage                    | New Recommended Command          | Notes |
|-------------------------------------|----------------------------------|-------|
| `make dev`                          | `xde dev`                        | Primary replacement |
| `make up`                           | `xde up`                         | - |
| `make reset-project`                | `xde reset`                      | Much better UX |
| `make clean`                        | `xde clean`                      | Stronger warnings |
| `make env`                          | `xde env`                        | - |
| Various build targets               | `xde build [--no-cache]`         | Simpler |
| `make shell`                        | `xde shell`                      | - |

During the transition period, the Makefile can become a thin wrapper that calls `xde` where possible, with deprecation warnings.

---

## Open Questions for Discussion

1. Should `xde env` have immediate subcommands (`show`, `regenerate`) or stay flat for v1?
2. Should `xde reset` support `--project-only` and `--db-only` flags in v1, or keep it as one targeted reset?
3. Do we want a `xde validate` command in v1 that runs schema + basic checks?
4. How aggressive should we be with deprecation warnings in the Makefile once core `xde` commands are real?
5. JSON output strategy: Should we add `--json` (or `--output json`) support? Recommendation: Add it selectively to diagnostic/inspection commands (`check`, `env`, future `config`) rather than every command. This is significantly more useful for agents than blanket application. A shared helper in `xde/utils/output.py` would keep it consistent.

---

## Recommendation

I recommend we **agree on this surface** (or a close variant) before doing significant further implementation work on individual commands. This will allow us to:

- Implement the `DockerComposeController` against a known interface.
- Write consistent help text and behavior.
- Update `AGENTS.md`, `docs/grok-playbooks.md`, and `DEV-JOURNAL.md` with confidence.
- Move toward Makefile retirement with a clear target.

Once agreed, we can move quickly into implementation.

---

**Next Step**: Please review and give feedback. Once we have alignment, I will:
- Update `AGENTS.md` and the playbooks with the final surface.
- Proceed with implementation (starting with strengthening `DockerComposeController` and wiring real behavior to the agreed commands).

This proposal is intentionally written to be easy to discuss and iterate on.