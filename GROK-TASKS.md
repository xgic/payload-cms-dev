# Grok Tasks

This file is the lightweight, informal task list for work that Grok Build should track.

**Rules:**
- This is **not** a replacement for GitHub Issues.
- Use it for quick reminders, small tasks, ideas, and things you want to do later without creating formal issues yet.
- Grok can (and should) edit this file directly when you say things like:
  - "Add 'Wire up real implementation for xde env' to the Grok tasks"
  - "Mark the reset dry-run task as done"
  - "Add this as a future idea"

---

## Next Up (High Priority)

### xde v1 Completion (Immediate Focus)
- [x] Finalize and lock the v1 command surface based on `docs/xde-v1-command-surface-proposal.md` (proposal marked "Finalized", docs/AGENTS.md aligned, CLI in src/xde/cli.py matches the 10 commands)
- [ ] Harden and complete highest-value commands:
  - [x] Full `xde dev` with real DB readiness check + auto-start services + actually launch pnpm dev inside project (using docker exec)
  - [ ] Complete `xde reset` with full logic migrated from `reset-project.py` (dry-run, compact, db setup, error handling, while keeping positive tone) (core done; full migration in progress)
  - [ ] Improve `xde check` with comprehensive DB + service health, structured output (DB check done; more in progress)
- [x] Create `docs/development-workflow.md` documenting commit discipline, testing requirements, and how to work during the Makefile → xde transition

### Testing Foundations (Step 3)
- [x] Add first meaningful test coverage focused on core `src/xde/core/` modules (EnvironmentContext and DockerComposeController) - unit tests with mocks for subprocess
- [x] Gate: ruff + pytest (test-xde retired with Makefile). xde core tests + make was shim, now direct pytest in CI.
- [x] Complete steps 1-6: port reset/env/schema, shims+warn, gate, remove Makefile (0.1.0 is xde-primary). See the removal commit.
- [x] xg/ reference directory: confirmed no need on 0.1.0 (moved to reference/xg-ais branch); stray untracked copy cleaned + documented in AGENTS pitfall.

### Ongoing / Previously Started
- [x] Implement basic functional `xde check`
- [x] Implement basic functional `xde env`
- [x] Wire logs, shell, and basic clean
- [x] Implement core `xde reset` with --dry-run / --yes / --rotate-credentials
- [x] Improve `xde dev` to auto-start services and give better guidance
- [x] Add real DB readiness checks (pg_isready) to check/dev
- [x] Add --json support to diagnostic commands (check, env)
- [x] Make xde available inside the container by default (postCreateCommand + venv); document optional host install (uv tool, platform-separated) as advanced only. Host install no longer in main Quick Start.

## Recently Completed

- [x] Removed or rephrased all negative comments about the Payload CMS setup process across the codebase and documentation (to maintain a positive, constructive relationship with the Payload team).

## Backlog / Ideas

- Consider adding `--json` support to diagnostic commands (`check`, `env`, etc.)
- Evaluate whether `xde env` should have subcommands in v1 (`show`, `regenerate`)
- Explore a lightweight "context dumper" helper for agents (e.g. `xde context` or a script)
- **Long-term vision**: Turn xde into a world-class Python library + framework (not just a CLI). Make core functionality importable so other Python projects (Ansible modules, custom automation tools, CI runners, etc.) can use xde's logic directly via API instead of shelling out. This enables much deeper integration and future-proofing.

- **Docker/Compose Interface Strategy (Future Consideration)**
  - Current approach (as of 2026): We are deliberately using a simple subprocess-based implementation to call the `docker` and `docker compose` CLI. The operations we perform today are relatively straightforward, so we do not need additional complexity at this stage.
  - We will keep the current implementation as long as it remains reliable.
  - We will periodically re-evaluate whether to rewrite `src/xde/core/docker.py` to use a more advanced interface (e.g. `python-on-whales`, the official Docker Python SDK, or a small Go helper binary using Docker's official Go Compose SDK).
  - This decision will be revisited when we encounter limitations or when we are ready to invest in a more sophisticated backend as part of the long-term goal of making `xde` a high-quality importable library/framework.
  - The public API should be kept stable to allow future backend changes with minimal impact.

### Testing & Automation Roadmap (High Priority Future Work)

**Goal**: Build world-class reliability and automation for this dev container template and the Payload CMS projects it generates.

Priorities (in rough order):
- Dramatically increase unit test coverage for all core logic in `src/xde/` (EnvironmentContext, DockerComposeController, reset logic, config handling, etc.).
- Add integration tests that exercise real Docker Compose operations and the complete development lifecycle.
- Implement end-to-end tests that bring up full environments and validate the generated Payload CMS applications (including browser-level validation where valuable).
- Build automatic staging build and deployment pipelines.

This work must follow the Collaboration Principles in `AGENTS.md`: positive and constructive framing at all times. Past experiences are only referenced when they provide concrete lessons that help avoid repeating specific mistakes.

## Done / Recently Completed

*(Add completed items here with date when marked done)*

---

## How to Use This File (For Grok)

When the user asks you to track something:

1. Add it under the appropriate section (usually "Next Up" or "Backlog").
2. Use clear, actionable language.
3. Optionally add a short note with context or a link to relevant docs.
4. When something is completed, move it to "Done" with the date. Note which commit delivered it.

Commit expectations (per AGENTS.md Collaboration Principles):
- Commits should represent logical, atomic units of change. Smaller commits (including single-file changes) are acceptable when they improve clarity.
- Every commit must deliver the complete change being made and pass linting and all relevant tests.
- Include relevant documentation updates in the same commit when they form part of the work.
- Local development commits may be granular. History should be cleaned (via rebase or squashing) before pushing or merging to the primary branch, following standard GitHub and open source practices.

Keep this file short and scannable. If something grows into a real feature or needs discussion, suggest creating a proper GitHub issue and reference it here.

When adding items, follow the Collaboration Principles defined in `AGENTS.md` (positive framing, focus on future value, reference past only when it prevents mistakes).

**Example entry:**
- [ ] Add `--json` flag to `xde check` (see discussion in proposal)

Last updated: [Grok will maintain this]