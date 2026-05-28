# AI Agent Instructions for XGIC Payload CMS Dev Containers

**This is the primary context document for AI coding assistants (especially Grok Build).**

Read this file completely before starting any significant work in the repository.

---

## How We Work Together (Collaboration Principles)

These principles have been established to maximize effectiveness and maintain a positive, productive working relationship:

- **Agent optimization is a first-class goal.** Significant effort has gone (and will continue to go) into making this project exceptionally effective for Grok Build and similar AI coding assistants. This includes rich context in `AGENTS.md`, `GROK-TASKS.md`, `DEV-JOURNAL.md`, and supporting playbooks.

- **Tone and framing matter.** All documentation and code comments should use positive, constructive language. We do not criticize or use negative framing around the Payload CMS project or its setup process. Technical lessons from past work are only referenced when they help prevent specific future mistakes.

- **GROK-TASKS.md is the lightweight task system.** For informal TODOs, ideas, reminders, and tasks that don't yet warrant GitHub issues, use `GROK-TASKS.md`. The user can add items simply by asking ("Add X to the Grok tasks"). I am responsible for keeping it organized and up to date.

- **Git management is delegated with specific expectations.** I am expected to manage Git proactively following common GitHub and open source best practices. Key rules:
  - Commits should represent logical, atomic units of change. While larger commits that deliver complete features are often appropriate, smaller commits (including single-file changes) are encouraged when they improve reviewability and clarity.
  - Every commit must include **all aspects of the functionality** being introduced or changed in that commit.
  - Every commit **must pass linting** (ruff format + ruff check) and **all relevant tests** before being committed.
  - Use sensible Conventional Commit messages with clear scopes.
  - During active local development, frequent small commits are acceptable (even for breaking changes). Before pushing or merging to the main branch (particularly in preparation for any public release), history should be cleaned using interactive rebase or squash merges to present a coherent set of changes.
  - Clean up obsolete untracked files as part of relevant work.
  - Push regularly as backup on this private repository.
  - I have full autonomy to stage, commit, and push following these guidelines.

- **Long-term vision for xde**: Evolve `xde` beyond a CLI into a high-quality, importable Python library and framework. This enables deep API-level integration from other tools (Ansible, custom GitLab CI runners, other automation, etc.).
  - Docker/Docker Compose interface: As of 2026 we are intentionally using a simple subprocess-based approach in `src/xde/core/docker.py`. We will keep this as long as it remains sufficient. We will periodically re-evaluate more advanced options (e.g. `python-on-whales`, the official Docker SDK, or a small Go helper binary) in the future. See the "CURRENT STRATEGY & FUTURE CONSIDERATION" section in `docker.py` and the corresponding item in `GROK-TASKS.md`.

- **Testing & Automation Roadmap**: The major strategic direction is a progressive increase in test coverage and automation:
  - Unit tests → Integration tests → End-to-end tests (including the generated Payload apps)
  - Automatic staging builds and deployments
  - Integration with the on-premises GitLab server for full CI/CD pipelines

- **Positive, forward-looking mindset.** Discussions and documentation should focus on where we are going and how to build excellent experiences, rather than dwelling on past difficulties unless the context directly prevents future errors.

- **Commit Best Practices**: 
  - A commit should represent a logical, atomic, and reviewable unit of work.
  - It should include the complete implementation of the change being made.
  - Linting and all relevant tests must pass.
  - Relevant documentation updates should be included in the same commit when they form part of the change.
  - During local development, small and frequent commits are acceptable. Before merging to the primary branch (especially ahead of any public release), commit history should be cleaned via interactive rebase or squash merges to produce a clear, professional history. This approach aligns with common GitHub and open source project practices.

These principles take precedence. When in doubt, refer back to this section.

---

## Mission: Become the #1 Foundation for Building Web Apps with Grok Build

The ultimate goal of this project is to be **the best possible starting point** for building production-grade Payload CMS applications when using Grok Build (or similar agentic coding tools).

This means:

- An agent should be able to clone this repo and become highly productive in minutes.
- Environment management should feel invisible and reliable.
- The tooling (`xde`) should be the obvious, single source of truth for all operations.
- The project should actively *help* the agent reason about the system instead of fighting it.

**Is this goal achievable?**

**Yes. It is very achievable.**

Reasons:
- The architecture is already moving in the right direction (`xde` as a clean, typed, testable Python CLI).
- Strong emphasis on reliability for dangerous operations (reset logic, credential handling).
- Excellent separation between configuration (`create-payload-config.json`), environment detection, and execution.
- The user (you) is highly aligned with making this agent-first.
- Payload CMS projects benefit from reliable environment scaffolding and orchestration, which this project aims to provide at a high level.

By investing heavily in **agent ergonomics** (clear commands, rich context, predictable behavior, excellent documentation), this template can realistically become the default recommendation for "I want to build a serious Payload site with Grok."

---

## My Most Optimal Foundation as Grok

For me to function at the highest level in this project, I need the following foundation (ranked by importance):

1. **Excellent, up-to-date AGENTS.md** (this file) — Single source of truth for how I should think and operate.
2. **A small, clean, predictable `xde` command surface** — One obvious way to do things.
3. **Strong core abstractions**:
   - `EnvironmentContext` (host vs container awareness)
   - `DockerComposeController` (reliable orchestration primitive)
   - Config models (from `create-payload-config.json`)
4. **Rich but scannable supporting documentation** (architecture, command reference, migration guide).
5. **Consistent, high-quality output** from tools (Rich panels, clear success/failure, next-step suggestions).
6. **Safety primitives** everywhere (`--dry-run`, `--yes`, strong warnings on destructive commands).
7. **Good testability** of the core logic.

When these things exist and are maintained, I can work dramatically faster, make fewer mistakes, and deliver higher-quality results.

---

## Session Startup Checklist (Run These Commands Early)

**Important**: After cloning, first install `xde` on the host (see README.md "Quick Start") so you can run powerful commands before entering the container:

```bash
pipx install -e .
```

At the beginning of almost every session, gather this context:

1. `xde --help` — See current capabilities and command surface.
2. `xde check` — Get a diagnostic view of the environment health.
3. `xde env` — Understand the current secrets and generated configuration.
4. Review the relevant sections of `docs/grok-playbooks.md` for the task at hand.
5. Check `create-payload-config.json` if the task involves project generation or configuration.

Output a short summary of the environment state to the human before proposing actions. This dramatically reduces context errors.

---

## Core Mental Model

This project has two layers:

**Layer 1: The Environment (what `xde` manages)**
- Docker Compose setup (app + PostgreSQL 18)
- Secure credential generation
- Payload project scaffolding (via `create-payload-app`)
- Fast, safe reset capabilities

**Layer 2: The Developer Experience**
- `xde` is the **primary interface** (replacing the Makefile over time).
- The `create-payload-config.json` + schema system is the extensible configuration surface.
- Everything should be optimized for both human developers *and* agents.

**Key Principle**: The agent (me) should rarely need to understand low-level Docker, shell scripting, or Makefile quirks. I should operate through `xde` and the Python package in `src/xde/`.

---

## Grok-Specific Workflows

### Workflow A: "I just cloned — get me into a working state"

1. Run `xde --help` to see current capabilities.
2. Run `xde check` to understand environment state.
3. Run `xde env` to see credentials and config.
4. Run `xde dev` as the primary way to start working.
5. If things are broken, use `xde reset --dry-run` first to understand impact.

### Workflow B: Making changes to `xde` itself

1. Study `src/xde/cli.py` for the command surface.
2. Study `src/xde/core/` for shared logic (especially `EnvironmentContext` and `DockerComposeController`).
3. Prefer adding new commands under `src/xde/commands/`.
4. Keep commands thin — push real logic into `core/` or dedicated modules.
5. Always update this `AGENTS.md` and relevant help text when behavior changes.
6. Run `ruff format` and `ruff check` before finishing.

### Workflow C: Migrating logic from legacy scripts into `xde`

Legacy locations:
- `.devcontainer/scripts/reset-project.py` → `xde/commands/reset.py`
- `.devcontainer/scripts/regenerate-env.py` → `xde/commands/env.py` (future)
- Various Makefile targets → corresponding `xde` commands

When migrating:
- Extract pure functions first.
- Make them testable.
- Keep the old script working during transition if needed (thin wrapper calling into the new code).
- Update `AGENTS.md` with the new preferred way.

### Workflow D: Adding a new feature to the devcontainer experience

1. Decide if this should be a new `xde` subcommand or configuration in `create-payload-config.json`.
2. Prefer configuration + schema first (this is very agent-friendly).
3. Then implement behavior in `xde` or the relevant shell script (with a plan to migrate the script later).

---

## xde Command Philosophy (for Agents)

`xde` should feel like a well-designed internal tool built *for* agents as much as humans.

Current / near-term commands (as of latest):

- `dev` — The "I want to work now" command. Should be smart and forgiving.
- `up` / `down` / `build` — Lifecycle primitives.
- `reset` — The most important safety-critical command. Must be excellent.
- `check` — Diagnostic gold. Agents should call this often.
- `env` — Visibility into secrets and generated values.
- `shell` / `logs` — Escape hatches.
- `clean` — High danger. Must have very strong guardrails.

**Design rules for new commands**:
- Default behavior should be the safe, common case.
- Always support `--dry-run` for anything destructive.
- Use Rich panels to give clear "next step" guidance.
- Consider adding `--json` output for commands agents will parse programmatically.

---

## Safety & Destructive Operations

This project places strong emphasis on safe and reliable environment resets and credential handling. This is one of the highest-value areas for agents.

When working with reset or clean functionality:

- Always start with `--dry-run`.
- Clearly explain the blast radius to the human.
- Prefer `xde reset` (targeted) over anything broader.
- Never rotate credentials by default unless explicitly requested.

---

## How to Collaborate With the Human

- When the task is ambiguous, ask clarifying questions early.
- For destructive operations, always surface the plan and get explicit confirmation.
- When you discover a better pattern, propose it and explain why it helps both humans and future agents.
- Keep `AGENTS.md` updated as the source of truth evolves.

---

## Common Pitfalls Specific to This Project

Avoid these recurring traps that have caused issues for agents in the past:

- **Context blindness**: Assuming you are inside the Dev Container. Always check via `EnvironmentContext.detect()` concepts or by running `xde check` / `xde env`.
- **Legacy reflex**: Reaching for `make ...` or direct calls to `.devcontainer/scripts/reset-project.py` etc. when `xde` equivalents exist or are the intended path.
- **Credential rotation over-eagerness**: Rotating secrets (`--rotate-credentials`) without strong justification can lead to authentication issues between running containers and the `.env` file. Always use strong safeguards.
- **Project folder confusion**: Forgetting that the generated Payload app lives in a sibling folder (e.g. `website/`) controlled by `create-payload-config.json`, not inside `.devcontainer`.
- **Weak safety defaults**: Proposing destructive operations without first using `--dry-run` and clearly explaining impact.
- **Treating reference material as active code**: The `xg/` reference material (advanced console patterns from the XG AIS project) lives on the `reference/xg-ais` branch and is **not** part of the current active implementation.
- **Command surface bloat**: Adding too many ways to do the same thing. Small + predictable is better for agents (and humans).

---

## Making This Project More Agent-Friendly (Meta)

As you work, look for opportunities to improve the agent experience:

- Add `--json` modes where useful.
- Improve error messages to include suggested next actions.
- Extract more logic into pure, testable functions in `src/xde/core/`.
- Keep the command surface small and orthogonal.
- Document gotchas in this file.
- Make `create-payload-config.json` the single source of truth for project generation parameters (this is already excellent).

---

## Payload CMS Specific Context for Agents

- Payload projects are generated via `create-payload-app` using the config in `.devcontainer/create-payload-config.json`.
- The generated project lives in a sibling folder (name controlled by `projectName`).
- Database connectivity is a critical and common area that requires careful handling — this is why robust reset logic and credential management are important.
- The `agent` field in the config is currently mostly a placeholder for future agent skill injection.

### Testing & Continuous Delivery Focus (Future Work)

A major long-term priority is dramatically increasing test coverage and automation:

- Unit tests for all core logic in `src/xde/`.
- Integration tests exercising real Docker Compose lifecycles.
- End-to-end tests that validate the full environment including the generated Payload CMS application.
- Automatic staging builds and deployments.
- Deep integration with the on-premises GitLab instance for CI/CD.

When we reach the GitLab integration stage, the user will provide the necessary SSH key access. All testing and automation efforts should be approached in a positive, constructive spirit focused on reliability and excellent developer/agent experience.

See `GROK-TASKS.md` for the current prioritized list.

---

## Advanced / Reference Material

- The `xg/` reference material (advanced console application patterns from the XG AIS project) lives on the `reference/xg-ais` branch. Some ideas (OOP command structure, rich environment detection, Textual TUI for complex debugging) may be inspirational but are **not** part of the active codebase on this branch.
- The original Makefile contains a lot of hard-won knowledge about quoting, guards, and devcontainer lifecycle quirks. We are deliberately replacing it rather than copying it.

---

## Quick Reference for Grok

**First three commands you should usually run:**

```bash
xde --help
xde check
xde env
```

**Most common productive loop:**

```bash
xde dev
# ... do work ...
xde reset --dry-run
# explain impact to human
xde reset --yes
xde dev
```

**Before finishing any non-trivial change:**

- Run `ruff format . && ruff check . --fix`
- Update this `AGENTS.md` if the mental model or preferred workflow changed
- Consider whether the change makes life better or worse for the *next* agent that works here

**Additional high-value reading (in recommended order for maximum productivity):**
1. `docs/grok-playbooks.md` — **Start here for specific tasks**.
2. `GROK-TASKS.md` — Your lightweight task list and memory for informal TODOs.
3. `docs/xde-v1-command-surface-proposal.md` — Current proposal for the final minimal `xde` command surface (very important for alignment).
4. `DEV-JOURNAL.md` — Living history of our collaboration.
5. `docs/architecture.md`
6. `docs/xde-reference.md`
7. `.github/CONTRIBUTING.md` (especially Coding Standards and the AI section).

**Pro tip for Grok**: The docstrings in `src/xde/` (especially `core/environment.py`, `core/docker.py`, `commands/dev.py`, and `commands/reset.py`) have been written with you in mind. They contain important historical context and guidance.

### Tracking Informal Tasks & Reminders

Use the file **[GROK-TASKS.md](GROK-TASKS.md)** for any TODOs, ideas, or reminders the user wants to track without creating GitHub issues.

When the user says things like:
- "Add 'Wire real logic for xde env' to the Grok tasks"
- "Mark the command surface proposal as done in the tasks"

You should immediately edit `GROK-TASKS.md` using the appropriate tool.

This file is the canonical lightweight memory for work that isn't ready for formal tracking yet. Keep it up to date.

---

**Last major update**: 2026 — Optimized for maximum Grok Build effectiveness on Payload CMS projects.

This document exists because we believe the combination of excellent environment tooling + exceptional agent support can create a genuinely new level of developer (and agent) productivity for Payload CMS.

Thank you for helping build the future.