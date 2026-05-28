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

- [ ] Finalize and agree on the v1 command surface from `docs/xde-v1-command-surface-proposal.md`
- [ ] Strengthen `DockerComposeController` with better real implementations
- [ ] Implement proper `xde reset` (migrate key logic from `reset-project.py`)
- [x] Implement basic functional `xde check`
- [x] Implement basic functional `xde env`
- [x] Wire logs, shell, and basic clean
- [x] Implement core `xde reset` with --dry-run / --yes / --rotate-credentials
- [x] Improve `xde dev` to auto-start services and give better guidance
- [x] Add real DB readiness checks (pg_isready) to check/dev
- [x] Add --json support to diagnostic commands (check, env)
- [x] Install xde on host via pipx and document installation for initial use after clone

## Recently Completed

- [x] Removed or rephrased all negative comments about the Payload CMS setup process across the codebase and documentation (to maintain a positive, constructive relationship with the Payload team).

## Backlog / Ideas

- Consider adding `--json` support to diagnostic commands (`check`, `env`, etc.)
- Evaluate whether `xde env` should have subcommands in v1 (`show`, `regenerate`)
- Explore a lightweight "context dumper" helper for agents (e.g. `xde context` or a script)
- **Long-term vision**: Turn xde into a world-class Python library + framework (not just a CLI). Make core functionality importable so other Python projects (Ansible modules, GitLab CI runners, custom automation tools, etc.) can use xde's logic directly via API instead of shelling out. This enables much deeper integration and future-proofing.

### Testing & Automation Roadmap (High Priority Future Work)

**Goal**: Build world-class reliability and automation for this dev container template and the Payload CMS projects it generates.

Priorities (in rough order):
- Dramatically increase unit test coverage for all core logic in `src/xde/` (EnvironmentContext, DockerComposeController, reset logic, config handling, etc.).
- Add integration tests that exercise real Docker Compose operations and the complete development lifecycle.
- Implement end-to-end tests that bring up full environments and validate the generated Payload CMS applications (including browser-level validation where valuable).
- Build automatic staging build and deployment pipelines.
- Deep integration with the on-premises GitLab server for CI/CD, including automatic staging environment creation and testing.

**Note**: SSH key access to the on-prem GitLab instance will be provided by the user when we reach the integration stage.

All testing and automation work should be done in a positive, forward-looking way focused on reliability and excellent experience for both human developers and AI agents. Past trial-and-error learnings should only be referenced when they help prevent specific classes of mistakes going forward.

## Done / Recently Completed

*(Add completed items here with date when marked done)*

---

## How to Use This File (For Grok)

When the user asks you to track something:

1. Add it under the appropriate section (usually "Next Up" or "Backlog").
2. Use clear, actionable language.
3. Optionally add a short note with context or a link to relevant docs.
4. When something is completed, move it to "Done" with the date.

Keep this file short and scannable. If something grows into a real feature or needs discussion, suggest creating a proper GitHub issue and reference it here.

**Example entry:**
- [ ] Add `--json` flag to `xde check` (see discussion in proposal)

Last updated: [Grok will maintain this]