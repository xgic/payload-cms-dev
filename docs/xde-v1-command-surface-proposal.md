# xde v1 Command Surface Proposal

**Date**: June 2026  
**Status**: Finalized for xde v1  
**Goal**: Define the minimal, final command surface for `xde` v1 that is simple, powerful, and sufficient.

**Decision**: This surface is now finalized. The CLI in `src/xde/cli.py` implements exactly these commands. All future xde v1 work targets this surface. See `docs/development-workflow.md` and the primary plan and platform issues/tasks for historical context.

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

This surface covers the large majority of the *valuable* daily functionality while being dramatically simpler and more predictable.

**Key Recommendations**:
- Drop the `stage` subcommand entirely for v1 (already removed in current code).
- Use flags instead of many similar commands (`--no-cache`, `--yes`, `--dry-run`, `--rotate-credentials`).
- Keep `env` as a lightweight top-level command with future subcommands.
- Use nested subcommands sparingly for extensibility (e.g. `setup payloadcms`) so the top-level `xde --help` stays concise.
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

| Command     | Purpose                                      | Key Flags                          |
|-------------|----------------------------------------------|------------------------------------|
| `dev`       | Smart "start working" experience             | (future: `--no-up`)                |
| `up`        | Start services                               | `--build`                          |
| `down`      | Stop services (volumes preserved)            | -                                  |
| `reset`     | Fast targeted reset (project + postgres)     | `--yes`, `--dry-run`, `--rotate-credentials` |
| `check`     | Health diagnostics                           | `--json` (future)                  |
| `build`     | Build images                                 | `--no-cache`                       |
| `logs`      | Follow logs                                  | -                                  |
| `shell`     | Interactive shell in main service            | -                                  |
| `env`       | Inspect and manage environment               | (future subcommands possible)      |
| `clean`     | Full environment cleanup (volumes + .env)    | `--yes`                            |

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
- Most lint/validate targets from the prior approach — these became direct `ruff` + `pytest` usage (and `xde` where it adds value).
- `exec` and `python` — Power-user commands. Can be added later as `xde exec` if needed.
- `init-env` and `create-payload` — These are mostly lifecycle hooks. `xde` can call into them, but they don't need to be direct user commands in v1.

---

## Rationale

### Why This Surface Is Efficient

- It covers the **daily development loop** extremely well (`dev`, `up`, `down`, `reset`, `check`).
- It gives agents a small, predictable vocabulary.
- It removes the biggest source of confusion from the prior broader automation surface (many similar targets, aliases, and internal details leaking into user space).
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

## Historical Note

This proposal (finalized 2026) defined the locked v1 surface now implemented in `src/xde/cli.py`. The design deliberately favored a small, predictable command set over the broader surface of the prior automation approach. Historical details of the transition live in the primary plan and platform issues/tasks (and git history).

---

## Open Questions for Discussion

1. Should `xde env` have immediate subcommands (`show`, `regenerate`) or stay flat for v1?
2. Should `xde reset` support `--project-only` and `--db-only` flags in v1, or keep it as one targeted reset?
3. Do we want a `xde validate` command in v1 that runs schema + basic checks?
4. (Historical) How to handle any remaining thin compatibility shims during the transition to the locked v1 surface? (Resolved by full removal of the prior automation layer.)
5. JSON output strategy: Should we add `--json` (or `--output json`) support? Recommendation: Add it selectively to diagnostic/inspection commands (`check`, `env`, future `config`) rather than every command. This is significantly more useful for agents than blanket application. A shared helper in `xde/utils/output.py` would keep it consistent.

---

## Recommendation

I recommend we **agree on this surface** (or a close variant) before doing significant further implementation work on individual commands. This will allow us to:

- Implement the `DockerComposeController` against a known interface.
- Write consistent help text and behavior.
- Update `AGENTS.md`, `docs/grok-playbooks.md`, and the primary plan and platform issues with confidence.
- Move toward a clean, locked command surface (achieved).

Once agreed, we can move quickly into implementation.

---

**Next Step**: Please review and give feedback. Once we have alignment, I will:
- Update `AGENTS.md` and the playbooks with the final surface.
- Proceed with implementation (starting with strengthening `DockerComposeController` and wiring real behavior to the agreed commands).

This proposal is intentionally written to be easy to discuss and iterate on.

All future work on xde must follow the Collaboration Principles in `AGENTS.md`.

**Important:** The Docker/Compose interface strategy is documented in `src/xde/core/docker.py` (section "CURRENT STRATEGY & FUTURE CONSIDERATION"). As of 2026 we are deliberately using a simple subprocess-based approach. We will periodically re-evaluate more advanced options in the future when our needs become more complex. The public API should be kept stable to allow future backend changes.