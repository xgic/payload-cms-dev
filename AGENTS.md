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

- **Long-term vision for xde**: Evolve `xde` beyond a CLI into a high-quality, importable Python library and framework. This enables deep API-level integration from other tools (Ansible, custom CI runners, other automation, etc.).
  - Docker/Docker Compose interface: As of 2026 we are intentionally using a simple subprocess-based approach in `src/xde/core/docker.py`. We will keep this as long as it remains sufficient. We will periodically re-evaluate more advanced options (e.g. `python-on-whales`, the official Docker SDK, or a small Go helper binary) in the future. See the "CURRENT STRATEGY & FUTURE CONSIDERATION" section in `docker.py` and the corresponding item in `GROK-TASKS.md`.
  - Release process as model: All 0.2.0+ release work (MongoDB support, AI-first features) is planned/executed/documented as an "external contributor simulation" (full GitHub Flow + fork/PR from CONTRIBUTING.md) + heavy Grok Build GitHub MCP automation (create_branch, issue_write, create_pull_request draft, push_files, etc.) **with mandatory human/developer verification and approval gates at every step**. This leads by example, produces clear living artifacts for contributors, and elevates reputation. See the approved session plan.md "Future Releases" section, the 0.2.0 external contributor guide, and updated GROK-TASKS/CONTRIBUTING for details. Update this vision when the process evolves.

- **Testing & Automation Roadmap**: The major strategic direction is a progressive increase in test coverage and automation:
  - Unit tests → Integration tests → End-to-end tests (including the generated Payload apps)
  - Automatic staging builds and deployments

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

**Important**: `xde` is installed by default inside the Dev Container (the primary environment). You do **not** need to install anything on the host for normal use.

At the beginning of almost every session (once inside the container), gather this context:

1. `xde --help` — See current capabilities and command surface.
2. `xde check` — Get a diagnostic view of the environment health.
3. `xde env` — Understand the current secrets and generated configuration.
4. Review the relevant sections of `docs/grok-playbooks.md` for the task at hand.
5. Check `create-payload-config.json` if the task involves project generation or configuration.

(Optional / advanced) If you need `xde` on the host before the container is open (e.g. for pre-container diagnostics), see the "Advanced: Installing xde on the Host (Optional)" section in README.md. It uses modern `uv tool install -e .` with platform-specific instructions.

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
- `xde` is the **primary (and only) interface**.
- The `create-payload-config.json` + schema system is the extensible configuration surface.
- Everything should be optimized for both human developers *and* agents.

**Key Principle**: The agent (me) should rarely need to understand low-level Docker internals or shell scripting quirks. I should operate through `xde` and the Python package in `src/xde/`.

---

## Grok-Specific Workflows

### Workflow A: "I just cloned — get me into a working state"

`xde` is available by default inside the Dev Container (after `Dev Containers: Reopen in Container`).

1. Open the folder in VS Code and select Reopen in Container when prompted.
2. Once inside, run `xde --help` to see current capabilities.
3. Run `xde check` to understand environment state.
4. Run `xde env` to see credentials and config.
5. Run `xde dev` as the primary way to start working.
6. If things are broken, use `xde reset --dry-run` first to understand impact.

(Optional advanced) For host-side `xde` commands before the container is open, see the optional host installation section in README.md.

### Workflow B: Making changes to `xde` itself

1. Study `src/xde/cli.py` for the command surface.
2. Study `src/xde/core/` for shared logic (especially `EnvironmentContext` and `DockerComposeController`).
3. Prefer adding new commands under `src/xde/commands/`.
4. Keep commands thin — push real logic into `core/` or dedicated modules.
5. Always update this `AGENTS.md` and relevant help text when behavior changes.
6. Run `ruff format` and `ruff check` before finishing.

### Workflow C: Migrating logic from legacy scripts into `xde`

The reset migration is complete:
- `.devcontainer/scripts/reset-project.py` (and its dedicated fidelity tests) have been removed as deprecated/outdated.
- Core behavior lives in `src/xde/commands/reset.py` + `src/xde/core/docker.py` (with targeted `up(services=...)` and `rm_service` helpers so reset can safely manage only the postgres volume without touching the caller's own container).

Historical note (for future similar migrations):
- Extract pure functions first.
- Make them testable.
- Remove the old script + its fidelity tests once the xde path is the canonical one and references have been swept.
- Keep the old script working during transition if needed (thin wrapper calling into the new code).
- Update `AGENTS.md` with the new preferred way.

### Workflow D: Adding a new feature to the devcontainer experience

1. Decide if this should be a new `xde` subcommand or configuration in `create-payload-config.json`.
2. Prefer configuration + schema first (this is very agent-friendly).
3. Then implement behavior in `xde` or the relevant shell script (with a plan to migrate the script later).

---

## xde Command Philosophy (for Agents)

`xde` should feel like a well-designed internal tool built *for* agents as much as humans.

Current / near-term commands (v1 surface, finalized per `docs/xde-v1-command-surface-proposal.md`):

- `dev` — The "I want to work now" command. Should be smart and forgiving.
- `up` / `down` / `build` — Lifecycle primitives.
- `reset` — The most important safety-critical command. Must be excellent.
- `check` — Diagnostic gold. Agents should call this often.
- `env` — Visibility into secrets and generated values.
- `shell` / `logs` — Escape hatches.
- `clean` — High danger. Must have very strong guardrails.

(See `DEV-JOURNAL.md` for historical transition details.)

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

**Preferred workflow for refining issues, PRs, architectural docs, strategic concepts, and planning with Grok Build (codified for efficiency and exemplarity):**

- **Early ideation and lightweight tracking**: Use `GROK-TASKS.md` for informal TODOs, ideas, reminders, and tasks that do not yet warrant formal GitHub issues. Record decisions, context, and collaboration history in `DEV-JOURNAL.md`. Use private session planning artifacts (e.g., the detailed plan document in the current Grok Build session) for complex, multi-phase reasoning and back-and-forth.

- **When a concept is ready for structured sharing, refinement, or formal tracking**: Draft the complete, high-quality Markdown content (full issue/PR body, proposal, or doc section) in the chat or session plan. After your explicit review and LGTM in this conversation, Grok will create it as a **Draft GitHub Issue** (or Draft PR where appropriate) directly on the target repository using connected MCP tools. The created artifact will carry "ai-draft" labeling (or equivalent), explicit human-gate language in the body (e.g., "This was prepared with Grok Build assistance. Human review and explicit approval required before any implementation steps, code changes, or further remote actions"), and full context/links.

- **Iteration and gates**: Refine the draft on GitHub itself (Grok can propose edits via tools or you edit directly). All remote actions (issue creation, updates, code pushes, etc.) remain under mandatory human/developer verification and approval gates, consistent with our external contributor simulation model.

- **Promotion to committed work or documentation**: Once approved, convert the draft to a real issue/PR, or extract mature content into committed documentation (e.g., `docs/strategy/`, architecture decision records, updates to CONTRIBUTING.md or this file) via a normal, atomic pure GitHub Flow pull request that passes all checks and human review.

- **For exemplary, forward-looking public repositories** (such as payload-cms-dev-container and future public repos): Strictly avoid temporary draft `.md` files or planning artifacts in the working tree. All design, strategic, and planning work surfaces as draft GitHub issues from the beginning. This ensures the collaboration method itself is clean, auditable, strictly forward-looking, and demonstrates 100% confidence in our processes with zero references to prior methodologies or transitions. Temporary files (if used during private ideation) must be cleaned before any port or bootstrap of a new repo.

**Hard Security Rule for Private Repositories (enforced across all Grok Build work)**:

**Zero exposure (absolute)**: No mentions, names, details, architectures, experiments, timelines, strategies, links, or any information that would reveal the existence, identity, or structure of any private repositories or private coordination hubs may ever be placed in any public XGIC repository (this repo, payload-cms-dev-container, or any other public one). This includes documentation, prompts, code, issues, PRs, READMEs, or any Grok output.

This is a **hard, non-negotiable security rule**. It enforces least privilege and prevents information disclosure. Violations are treated as security incidents and must be corrected immediately (clean the public repo, reinforce prompts and templates).

**Where private coordination lives**: All detailed repo coordination rules, multi-repo planning, internal orchestration playbooks, GitLab experiments, and anything involving private repos or sensitive strategy live *exclusively* in the authoritative private master AI orchestration repository. Public repositories and public sessions must remain completely silent on private details and structures.

**Enforcement**:
- Any prompt or context given to Grok for work that could touch multi-repo or strategy must restate this rule abstractly.
- Public AGENTS.md, playbooks, and templates contain only this high-level boundary reminder.
- The full living playbook (with exact commands, session patterns for GitLab primary, glab usage, multiple focused sessions, etc.) is maintained only in the private hub.
- Human review of any proposed public content is required to prevent leakage.

Public work uses GitHub (rich MCP + gh for external contributor simulations, living guides, exemplary OSS process). Private primary instance (your GitLab) hosts the real orchestration hub and most private repos. Grok sessions against the private hub use terminal + glab/git for all operations.

This approach lets you leverage GitLab as the primary instance for your many private repos while still using GitHub where it adds the most value (public demonstration + powerful MCP automation).

Update this guidance (and related sections in CONTRIBUTING.md, playbooks, etc.) whenever our collaboration patterns or standards evolve.

---

## Common Pitfalls Specific to This Project

Avoid these recurring traps that have caused issues for agents in the past:

- **Context blindness**: Assuming you are inside the Dev Container. Always check via `EnvironmentContext.detect()` concepts or by running `xde check` / `xde env`.
- **Legacy reflex**: Reaching for old/deprecated scripts or direct low-level commands (e.g. raw `docker compose` or shell) instead of the `xde` equivalents.
- **Credential rotation over-eagerness**: Rotating secrets (`--rotate-credentials`) without strong justification can lead to authentication issues between running containers and the `.env` file. Always use strong safeguards.
- **Project folder confusion**: Forgetting that the generated Payload app lives in a sibling folder (e.g. `website/`) controlled by `create-payload-config.json`, not inside `.devcontainer`.
- **Weak safety defaults**: Proposing destructive operations without first using `--dry-run` and clearly explaining impact.
- **Treating reference material as active code**: The `xg/` reference material (advanced console patterns from the XG AIS project) lives on the `reference/xg-ais` branch and is **not** part of the current active implementation. (Stray untracked copy on 0.1.0 working tree was cleaned up as part of this check.)
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

All testing and automation efforts should be approached in a positive, constructive spirit focused on reliability and excellent developer/agent experience.

See `GROK-TASKS.md` for the current prioritized list.

---

## Advanced / Reference Material

- The `xg/` reference material (advanced console application patterns from the XG AIS project) lives on the `reference/xg-ais` branch. Some ideas (OOP command structure, rich environment detection, Textual TUI for complex debugging) may be inspirational but are **not** part of the active codebase on this branch.
- Early automation contained hard-won lessons about quoting, guards, and devcontainer lifecycle quirks. The current `xde` implementation was written cleanly rather than carrying everything forward.

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