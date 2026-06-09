# Development Workflow

This document defines how we work on this project, with a particular emphasis on maintaining high quality while moving quickly toward the goal of retiring the Makefile in favor of `xde`.

These guidelines apply to both human contributors and AI-assisted development (Grok Build).

## Core Principles

- **Reliability over speed**: Every change that lands on the primary branch must be reliable.
- **Agent productivity is a first-class concern**: The project should remain easy for Grok Build (and similar tools) to work with effectively.
- **Positive, constructive tone**: We focus on building excellent experiences rather than criticizing past approaches (especially anything related to Payload CMS).

## Commit Discipline

### What Makes a Good Commit

- A commit must represent a **logical, atomic unit of change**.
- Smaller, focused commits (including single-file changes) are perfectly acceptable and often preferred when they make the change easier to understand and review.
- Every commit **must**:
  - Deliver the complete functionality being introduced or modified in that commit.
  - Pass linting (`ruff format` and `ruff check`).
  - Pass all relevant tests.
  - Include updates to documentation (including `AGENTS.md`, `GROK-TASKS.md`, `DEV-JOURNAL.md`, and user-facing docs) when they are part of the work.

### Local vs Published History

- During active local development, frequent granular commits are acceptable (even for breaking changes).
- Before pushing or opening a pull request to the primary branch (especially in preparation for any public release or history reset), the commit history should be cleaned using interactive rebase (`git rebase -i`) or squash merges so that the published history presents a clear, professional narrative.
- This approach follows common GitHub and open source best practices.

### Conventional Commits

All commits must use the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Testing Requirements

Before every commit that touches code:

1. Run the project's linting and test suite (via `make validate` or equivalent when available).
2. All tests must pass.
3. Linting must be clean.

We are actively building toward the following testing progression:
- Unit tests for core logic in `src/xde/core/`
- Integration tests exercising real Docker Compose behavior
- End-to-end tests validating full environments and generated Payload applications

## Working with the Makefile During Transition

(Makefile removed in 0.1.0; all via xde):

- Prefer using `xde` commands for new work.
- When modifying existing Makefile targets, consider whether the logic can move into `xde` instead.
- The Makefile may become a thin compatibility layer with deprecation warnings over time.
- Never introduce new complex logic into the Makefile unless there is a strong short-term reason.

## Docker and Docker Compose Interface

As of 2026, `src/xde/core/docker.py` uses a simple subprocess-based
approach to call the `docker` and `docker compose` CLI. The operations
we perform are relatively straightforward, so we do not need much
additional complexity at this stage.

We will keep the current implementation as long as it remains reliable.
We will periodically re-evaluate whether to rewrite this module to use
a more advanced interface (such as `python-on-whales`, the official
Docker Python SDK, or a small Go helper binary) in the future.

This decision is tracked in:
- `src/xde/core/docker.py` (section "CURRENT STRATEGY & FUTURE CONSIDERATION")
- `GROK-TASKS.md` (Docker/Compose Interface Strategy item)

The public API should be kept stable to allow future backend changes
with minimal impact.

## Working with AI Assistants (Grok Build, etc.)

- Follow the [Collaboration Principles](AGENTS.md#how-we-work-together-collaboration-principles) defined in `AGENTS.md`.
- Use `GROK-TASKS.md` for informal task tracking.
- Keep `DEV-JOURNAL.md` updated with significant decisions and progress.
- All work must follow the commit discipline described in this document.

## Branching and Pull Requests

- Work on short-lived feature branches.
- Keep the primary branch (`main` / `0.1.0`) in a releasable state at all times.
- Open pull requests for review when work is complete and has passed the commit requirements above.

## Commands to Run Before Committing

Before committing code changes:

```bash
# Recommended
make validate

# Minimum (when make validate is not yet fully available)
ruff format .
ruff check .
pytest -q   # or the relevant test subset for the change
```

All linting and tests must pass cleanly.

---

This document is the authoritative reference for our development process. Update it when our practices evolve.