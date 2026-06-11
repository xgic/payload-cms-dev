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
  - [x] Complete `xde reset` (targeted postgres volume handling, pre-stop for reliable volume removal, public-API targeted up so reset from inside the dev container does not recreate its own container, IF NOT EXISTS + safe wrapper for DB, clean output). Legacy reset-project.py + fidelity tests removed as deprecated. Full migration complete.
  - [x] `xde setup payloadcms` (nested under setup for future components without top-level bloat; modular + testable logic in core/project.py; wired to reset final step + thin fail-fast postStart shim).
  - [ ] Improve `xde check` with comprehensive DB + service health, structured output (DB check done; more in progress)
- [x] Create `docs/development-workflow.md` documenting commit discipline, testing requirements, and current workflows (xde-primary)

### Future Releases (0.2.0 and Beyond) - External Contributor Simulation + AI Automation
- [x] **0.2.0 Release planning + branching finalization + 0.1.0 merge (LGTM + final user directive)**: Conventional docs commit(s), 0.1.0 commits rebased into logical units (test refresh + release planning) and merged/pushed to main (671a8e5 + origin update), 0.1.0 confirmed passing all required testing and fully working for its initial Postgres dev env + xde scope (ruff clean, xde check/env healthy, no violations, git history per AGENTS). Separate Git repo advice for generated Payload dir delivered (Vercel/Codespaces/OSS etc.; see DEV-JOURNAL and plan). Adopted semantic `release/0.2.0` long-lived accumulation branch model (PRs target it until full release complete, then merge to main); all docs updated for the exact process (CONTRIBUTING, living guide, AGENTS, this file, plan, PR template already had the release type). Transitional artifacts (feat/0.2.0-mongodb-support + draft issues #1-3 + draft PR #4) closed/deleted per sole-dev "delete if can't cleanly update to prevent confusion" (audit comments + MCP/terminal; new `release/0.2.0` created from approved main; transparent notes in guide + plan + journal). First record commit on release/0.2.0 (docs + strategy + advice + execution). Human checkpoint required before further slices. (See approved plan "Final User Directive & Approval" + execution notes for full details.)
- [x] **0.2.0 Release: Official MongoDB / Multi-Adapter Support** (high-level plan in session plan.md; executed following the living guide + RELEASE_CHECKLIST on `release/0.2.0`). (Planning + docs/process artifacts + cleanup complete; core impl slices landed.)
  - [x] Config + schema: mongodb example added to create-payload-config.json; schema support leveraged (dbAdapter enum).
  - [x] Docker infra: Mongo service + profiles in docker-compose.yml; mongosh client in Dockerfile.
  - [x] xde logic: docker.py profile + adapter-aware db_ready/volume/service; reset/env generalized for mongo (postgres default preserved).
  - [ ] Full validation + release: switch config/test with mongodb, xde setup/reset/dev + E2E on generated app (no Postgres regression); finalize living guide; merge to main + tag + GitHub Release (using the now-standard post-merge tagging task).
  - [ ] **Standard post-merge automated task (for 0.2.0 and all future releases)**: After human approval of the final `release/0.X.0` → `main` merge (the key gate that the release scope is complete), Grok proposes the exact annotated tag + GitHub Release command (preferably `gh release create` on the precise merge commit, with message derived from the living guide + RELEASE_CHECKLIST). Human approves the command/message. Grok executes via `run_terminal_command`, pushes, and confirms the tag points to the correct commit. This is now codified as a repeatable automated step (see updated RELEASE_CHECKLIST.md and the living guide's Grok automation examples).
- [ ] **0.3.0 Release: AI-First Completeness & Polish** (high-level in plan.md; build on 0.2.0 multi-DB).
  - [ ] Context & Agent Ergonomics: Improve AI context detection (template vs generated app, extend EnvironmentContext, env markers in devcontainer.json). Add `xde context` dumper. More --json on commands (check, env, setup, reset). Safety (--dry-run/--yes everywhere).
  - [ ] Library / Framework: Extract more core (project, docker, env) as importable with examples/ (Ansible, CI, external tools). Add docs showing direct `from xde.core...`. Stable public API notes.
  - [ ] Testing Roadmap: Advance skeletons to real integration tests (Docker Compose lifecycles), full E2E (generated app validation with HTTP + future Playwright for Payload admin/frontend). `xde validate` / `xde lint` commands. Higher coverage, property/golden tests.
  - [ ] Multi-Env & Polish (build on 0.2): `stage` namespace (`xde stage up/dev`). Full multi-adapter maturity. Maintenance commands (`xde schema` enhancements, `xde clean`).
  - [ ] Interactive/Advanced: Explore Textual TUI (`xde tui`). Richer output, error recovery.
  - [ ] Ecosystem & CI: CI templates using xde. Automatic staging pipelines (per roadmap). Support more create-payload-app options via config.
  - [ ] Grok AI Automation: Use MCP tools for all OSS tasks (draft issues/PRs from "external fork" simulation, file updates via `create_or_update_file`/`push_files`, milestone management). Require human/developer verification/approval for every create/merge action. Log all steps for audit/reputation.
  - [ ] Reputation/Examples: Each release (0.3.0+) produces living examples in docs (following the 0.2.0 external + AI template). Update GROK-TASKS "Done", CONTRIBUTORS.md, etc. via automation where possible. Include the standard annotated tag + GitHub Release creation (with human gate after the final merge) as part of the example.
- [ ] Move/adapt existing backlog (context dumper, --json, library vision, testing E2E, Docker strategy) into the 0.2/0.3 sections above as sub-tasks.
- [ ] Add note in GROK-TASKS on the AI-first release process: "All future release work (0.2.0+) is executed and documented as external contributor simulation (CONTRIBUTING.md steps) + heavy Grok Build GitHub MCP automation (create_issue, create_pull_request draft, etc.) with mandatory human verification gates at each step. This leads by example and elevates XGIC reputation."

### Testing & Automation Roadmap (High Priority Future Work)

### Testing Foundations (Step 3)
- [x] Add first meaningful test coverage focused on core `src/xde/core/` modules (EnvironmentContext and DockerComposeController) - unit tests with mocks for subprocess
- [x] Gate: ruff + pytest. Direct pytest in CI (no legacy shims).
- [x] Complete the core xde v1 migration (reset, env, schema, shims, gates). 0.1.0 established xde as the single source of truth. See the relevant commits.
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

- [x] Test coverage verification baseline on 0.1.0 (post-setup-payloadcms + legacy removal): 33 focused tests, 53% on src/xde. Implemented prioritized recs 1-8 (expanded pure tests + dedicated test_project.py, extracted compute_synced/resolve helpers, integration + e2e skeletons, direct core imports for library vision, CI coverage surfacing on src/xde, GROK-TASKS note). See session plan.md for full report + gaps.
- [x] (Related) Refresh of TESTING.md to align with current xde-primary + unit→int→E2E + library roadmap. Hygiene: stale legacy artifacts cleaned; website/ remains untracked per direction.

*(Add more completed items here with date when marked done)*

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