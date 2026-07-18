# Contributing to `payload-cms-dev-containers`

**Project**: [XGIC/payload-cms-dev-containers](https://github.com/XGIC/payload-cms-dev-containers)  
**Purpose**: A production-grade, open-source toolkit that enables the rapid creation and setup of highly optimized **Payload CMS** development environments using **Visual Studio Code Dev Containers** orchestrated via **Docker Compose**.  

We welcome contributions from the open-source community. Whether you are fixing a bug, adding support for a new Payload CMS version, improving Docker performance, enhancing documentation, or proposing architectural improvements, your work directly advances developer productivity across the Payload CMS ecosystem.

By participating, you agree to abide by our [Code of Conduct](#code-of-conduct) and the [Contributor License Agreement](#contributor-license-agreement) (implicitly accepted upon submission of a pull request).

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Coding Standards & Best Practices](#coding-standards--best-practices)
- [Development Environment Setup](#development-environment-setup)
- [GitHub Flow & Branching Strategy](#github-flow--branching-strategy)
- [Step-by-Step Guide: Initiating a New Feature Branch (GitHub Free Account)](#step-by-step-guide-initiating-a-new-feature-branch-github-free-account)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Reporting Bugs & Requesting Features](#reporting-bugs--requesting-features)
- [Contributor License Agreement](#contributor-license-agreement)
- [Recognition](#recognition)
- [For AI Coding Assistants](#for-ai-coding-assistants)

### Subsections under Development Environment Setup
- [Local Development Commands](#local-development-commands)
- [Debugging & Logging](#debugging--logging)
- [Contributing to the Automation Logic](#contributing-to-the-automation-logic)
- [Linting & Quality](#linting--quality)

## Code of Conduct

We follow the [Contributor Covenant Code of Conduct (v2.1)](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).  
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project maintainers at `conduct@xgic.net`.

## Coding Standards & Best Practices

This section outlines the standards that apply specifically to **this repository** (a Dev Container + Docker Compose + automation tooling project).

**Start here**: See the [Code Style Quick Reference](#code-style-quick-reference) for the most important rules at a glance. The most important formatting rule is the [80-character line length limit for code files](#line-length-80-characters).

**AI assistants**: Read [AGENTS.md](AGENTS.md) **first**. Also see `docs/architecture.md` and multi-repo standards at https://github.com/xgic/ai. CLI implementation lives in modular packages — not in this template ([ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md)).

### Repository focus
Contributions to this repo typically involve:
- Dockerfiles and Docker Compose files
- Thin shell scripts (Bash) that delegate to **XGIC CLI** (`xgic`)
- YAML configuration (Dev Container, GitHub Actions, Dependabot)
- Template smoke tests and documentation
- **Not** new CLI libraries or an in-tree `xde` package (contribute those to [xgic/cli](https://github.com/xgic/cli), [xgic/dev-cli](https://github.com/xgic/dev-cli), or [xgic/payload-cms-cli](https://github.com/xgic/payload-cms-cli))

### Required standards

- **Dev Containers**: Prefer working inside the provided Dev Container. Test changes inside the container before opening a PR.
- **Docker**: Follow official [Docker Best Practices](https://docs.docker.com/build/building/best-practices/). Prefer multi-stage builds and minimize image size where reasonable.
- **Shell scripts**:
  - All `.sh` files must pass `shellcheck`.
  - Prefer POSIX-compliant syntax when practical. Use `set -euo pipefail` (or `set -e`) appropriately.
  - Scripts in `.devcontainer/scripts/` should remain thin orchestration layers (e.g. `exec xgic payload setup`). Complex CLI logic belongs in modular packages.
- **Python**: Template consumer tests only; follow PEP 8 / project ruff config. Install modular CLI from **PyPI** pins via `uv`.
- **YAML & GitHub Actions**: Use consistent indentation (2 spaces). Validate workflows with `actionlint` when changing `.github/workflows/`.
- **Documentation**:
  - Update `README.md` when user-facing behavior changes.
  - Update this file when contribution processes change.
  - Living docs use **XGIC CLI** only (no dual brand).

### Recommended practices
- Keep thin bash wrappers (`setup-payload.sh`, etc.) minimal — typically `exec xgic …`.
- Prefer configuration via `create-payload-config.json` (JSON Schema IntelliSense) over hardcoding values in scripts.
- Test with: `uv pip install -e ".[dev]" && uv run pytest -q`, plus manual `xgic check` / `xgic payload env` / `xgic payload reset --dry-run` / `xgic payload dev` inside the container.

All contributors are expected to review this document before submitting code.

### Line Length (80 characters)

**This rule applies only to code files.**

The maximum line length in this project is **80 characters** for all code. This limit improves readability in terminals, side-by-side diff views, git blame output, code review tools, and accessibility (screen readers, narrow windows).

#### What counts as a "code file"

The 80-character limit applies to:
- Python (`.py`)
- Shell scripts (`.sh`, `.bash`)
- TypeScript and JavaScript (`.ts`, `.js`, `.tsx`) — especially in `.devcontainer/config/`
- Dockerfiles (`Dockerfile*`)
- YAML workflow and configuration files (`.yml`, `.yaml`) — where reasonable (see exceptions)
- TOML configuration (`pyproject.toml`, etc.)
- Any other human-maintained source files that contain logic or configuration

#### What does **not** follow the 80-character rule

**Markdown documentation files (`.md`, `.markdown`)** are explicitly **exempt**.

- Long lines in prose, tables, code blocks inside docs, and URLs are acceptable and often preferable.
- Wrapping Markdown text with hard line breaks harms readability in web browsers, GitHub rendering, and VS Code Markdown preview.
- Example files that happen to be Markdown (e.g. reference material previously in `xg/examples/textual/*.md`, now on the `reference/xg-ais` branch) are treated as documentation.

Other justified exceptions (use sparingly and document why when non-obvious):
- Long URLs or URIs that cannot reasonably be shortened (especially in `$id` fields, documentation strings, or comments referencing external resources).
- Certain JSON Schema `description` values (these are user-facing documentation rendered by editors).
- Long string literals in tests that represent real-world data (e.g. large JSON fixtures, certificate material, or exact error output).
- Base64-encoded values, cryptographic hashes, or other opaque binary data represented as strings.
- (Historical) Decorative ASCII art or rule lines in old Makefiles when they served a clear visual purpose.

#### Enforcement and Tooling

- **Python**: Ruff is configured with `line-length = 80` in `pyproject.toml`. The `E501` rule is active (not ignored globally). Use `# noqa: E501` only for the rare justified exceptions listed above, and prefer a comment explaining why.
- **Shell**: `shfmt` and ShellCheck runs do not currently enforce hard line length, but contributors should still respect the 80-character guideline manually for readability.
- **Other languages**: Follow the rule manually. When a linter supports it (e.g. yamllint), it may be left disabled for practicality (see `.github/workflows/lint.yml` for current yamllint settings).
- **Markdown**: No automated wrapping. Write naturally for human readers in browsers and preview panes.

#### Practical guidance for developers

When a line of code approaches 80 characters:
1. Use the language's standard line continuation (Python parentheses, backslashes in shell, etc.).
2. Extract a variable or constant.
3. Break long strings with implicit concatenation or `textwrap.dedent`.
4. Only use a noqa / exception comment when none of the above produce clearer code.

If you are unsure whether a long line is justified, ask in the pull request or open a discussion. Maintainers will happily help find a clean solution.

### Code Style Quick Reference

This is the short, scannable version of the rules that matter most when contributing. For full explanations, rationale, and edge cases, see the detailed sections above and below.

**Core principle**: Match the style of surrounding code. When in doubt, run the project's linters and formatters.

#### At a Glance

- **Line length**: **80 characters maximum for all code files** (Python, Shell, TypeScript in `.devcontainer/config/`, Dockerfiles, YAML, etc.).
  - **Markdown files are explicitly exempt**. Write documentation naturally for web browsers, GitHub rendering, and VS Code Markdown preview. Do not add hard line breaks to prose.
  - (Historical Makefiles are no longer present; the rule remains for other code files.)
- **Python**: Ruff is the single source of truth for formatting and linting.
- **Shell scripts**: Prefer POSIX-compliant syntax. All `.sh` files must pass ShellCheck.
- **TypeScript config**: Follow existing patterns in `.devcontainer/config/types.ts` and `generate_schema.py`.
- **Commits & PRs**: Follow Conventional Commits. Commits should represent logical, atomic units of change. Smaller commits (including single-file changes) are acceptable when they improve reviewability. See the Collaboration Principles in `AGENTS.md` for agent-driven work.
- **Documentation**: Clarity for human readers (in browsers and previews) takes precedence over strict line wrapping.

#### Commands to Run Before Committing

```bash
# Format and lint Python (enforces 80-char limit for code)
ruff format .
ruff check . --fix

# Lint shell scripts (when shell changes are made)
# shellcheck is available inside the Dev Container
shellcheck .devcontainer/scripts/*.sh .devcontainer/scripts/lib/*.sh 2>/dev/null || true
```

#### Good vs. Bad Examples

**Python — line length (must wrap at 80 chars)**

Good:
```python
def create_environment_context(
    cwd: Path | None = None,
) -> EnvironmentContext:
    ...
```

Bad:
```python
def create_environment_context(cwd: Path | None = None) -> EnvironmentContext:  # exceeds 80 characters
    ...
```

**Markdown documentation — long lines are preferred**

Good (natural reading flow in browsers and previews):
> This is a production-grade toolkit that enables the rapid creation of optimized Payload CMS development environments using Dev Containers + Docker Compose.

Bad (unnecessary hard wraps hurt readability):
> This is a production-grade toolkit that enables the rapid creation  
> of optimized Payload CMS development environments using Dev Containers  
> + Docker Compose.

#### When Rules Conflict

Prefer readability and consistency with nearby code over dogmatic adherence. If a rule produces clearly worse code, add a short comment explaining the exception and open a discussion if it happens often.

## Development Environment Setup

The project itself is designed to be self-hosting. We strongly recommend using the **Dev Container** provided by this repository for all development work. This guarantees identical build, test, and lint environments for every contributor.

1. Fork the repository (see branching guide below).
2. Open your fork in **Visual Studio Code**.
3. VS Code will automatically detect the `.devcontainer/devcontainer.json` and prompt you to "Reopen in Container".
4. Once inside the container, run:
   ```bash
   docker compose up -d
   ```
5. The Payload CMS instance will be available at `http://localhost:3000`.

### Local development commands

After entering the Dev Container, use **XGIC CLI** (`xgic`) and direct tools:

| Command | Purpose |
|---------|---------|
| `xgic --help` / `xgic --version` | Top-level help / version |
| `xgic check` | Health diagnostics (services / environment) |
| `xgic env` | Generic environment status |
| `xgic payload env` | Payload CMS env status; `--regenerate --yes` for secrets |
| `xgic payload dev` | Recommended daily command: smart Payload app start |
| `xgic payload reset --dry-run` | Preview targeted reset (project + volume) |
| `xgic payload setup` | Ensure / recreate the Payload project (idempotent) |
| `uv pip install -e ".[dev]" && uv run pytest -q` | Template smoke tests |

See [AGENTS.md](AGENTS.md) and [TESTING.md](TESTING.md). CLI implementation docs live in the modular package repos.

### Debugging & logging

Control verbosity of setup scripts with `LOG_LEVEL` (`DEBUG`, `INFO`, `WARN`, `ERROR`):

```bash
# postStart hook (thin wrapper: exec xgic payload setup)
LOG_LEVEL=DEBUG bash .devcontainer/scripts/setup-payload.sh

LOG_LEVEL=warn bash .devcontainer/scripts/init-env.sh
```

### Contributing to automation

- `setup-payload.sh` → thin `exec xgic payload setup`.
- Payload project ensure / reset / Docker Compose lifecycle → modular packages (payload-cms-cli, dev-cli), not this tree.
- Prefer extending `create-payload-config.json` (+ schema) over hardcoding behavior.
- Keep bash scripts thin; test with `uv run pytest` + manual `xgic payload reset --dry-run` / `xgic payload dev` flows.

### Linting & quality

- **Shell**: `shellcheck`, `shfmt` (CI)
- **Workflows**: `actionlint` (CI)
- **YAML**: `yamllint` (CI)
- **Python tests**: `uv run pytest` (template smoke; see TESTING.md)
- **Release Validation**: Dev Container image build + XGIC CLI smoke (CI)

Local smoke:

```bash
uv pip install -e ".[dev]"
uv run pytest -q
uv run xgic --version
```

## Branching Strategy and Protected Branches (0.2.0+)

The project uses a pragmatic hybrid model that supports both ongoing development and disciplined major releases:

- `main` is the ultimate long-lived "source of truth" (releases, tags, and the history that guarantees reproducible dev containers). It is protected (see `docs/branch-protection.md`).
- For each major release cycle we use a semantic long-lived accumulation branch (e.g. `release/0.2.0`). All work, PRs (including external contributor simulations and Grok Build automation), and validation target this branch until the full scope (code + tests + docs + examples) is complete. Only then do we perform the final merge `release/0.X.0` → `main` + tag.
- Short-lived branches (`feat/...`, `fix/...`, `docs/...`, etc.) are created from the current base (usually the active release branch or `main`) and always merged via PR.

**Branch naming convention** (enforced via Conventional Commits tooling):
- `feat/...` – new features or enhancements
- `fix/...` – bug fixes
- `docs/...` – documentation changes
- `refactor/...` – code refactoring without functional change
- `test/...` – adding or updating tests
- `chore/...` – build, CI, or tooling changes
- `release/...` – used for the long-lived accumulation branches during a release cycle

Protected branch rules (enforced via repository settings / rulesets) require passing status checks and at least one approving review before merging to `main` or an active `release/*` branch. See the full policy and setup guidance in [docs/branch-protection.md](../docs/branch-protection.md). This policy is deliberately compatible with (and reinforces) the atomic-commit + human-gate + Grok automation patterns described in `AGENTS.md` and the release living guides.

## Step-by-Step Guide: Initiating Work as an External Contributor (GitHub Free Account)

GitHub Free accounts do **not** grant direct push access to organization repositories. Therefore, all external contributors **must** use the **Fork + Pull Request** workflow. The following guide is tailored specifically for contributors to `XGIC/payload-cms-dev-containers` and adheres to GitHub’s official best practices, the fork model, and Conventional Commits.

During an active release the base branch for your PRs will be the current `release/0.X.0` (see the release-specific living guide). For general/small contributions it will be `main` or the tip of the active release branch.

### Step 1: Fork the Repository
1. Navigate to [https://github.com/XGIC/payload-cms-dev-containers](https://github.com/XGIC/payload-cms-dev-containers) in your browser.
2. Click the **Fork** button in the top-right corner.
3. Select your personal GitHub Free account as the destination.
4. Once the fork completes, you will be redirected to `https://github.com/YOUR-USERNAME/payload-cms-dev-containers`.

### Step 2: Clone Your Fork Locally
```bash
git clone https://github.com/YOUR-USERNAME/payload-cms-dev-containers.git
cd payload-cms-dev-containers
```

### Step 3: Add the Upstream Remote
This allows you to keep your fork synchronized with the official repository:
```bash
git remote add upstream https://github.com/XGIC/payload-cms-dev-containers.git
git remote -v   # verify remotes
```

### Step 4: Fetch the Latest Upstream Changes
Always start from the current base (usually `main` or the active `release/0.X.0`):
```bash
git fetch upstream
git checkout main   # or the relevant release branch
git merge upstream/main   # or git rebase upstream/main
git push origin main
```

### Step 5: Create a New Feature / Fix Branch
```bash
git checkout -b feat/descriptive-feature-name
```
**Examples**:
- `feat/add-payload-3-0-support`
- `fix/docker-compose-healthcheck`
- `docs/improve-devcontainer-readme`

Branch names must be lowercase, use hyphens, and be descriptive.

### Step 6: Make Your Changes
- Work exclusively inside the Dev Container (recommended).
- Follow the [Coding Standards](#coding-standards--best-practices) below.
- For human contributors: Keep changes reasonably scoped.
- For agent-driven work: Commits should represent logical, atomic units of change (smaller commits, including single-file changes, are acceptable when they improve clarity). All commits must pass linting and relevant tests. See the Collaboration Principles in `AGENTS.md`. Local development commits may be granular; history should be cleaned before pushing or merging to a protected branch.

### Step 7: Stage, Commit, and Push
Use **Conventional Commits** (see section below):
```bash
git add .
git commit -m "feat: add support for Payload CMS v3.0"
git push origin feat/descriptive-feature-name
```

### Step 8: Open a Pull Request
1. Go to your fork on GitHub.
2. Click **Compare & pull request**.
3. Ensure the base repository is `XGIC/payload-cms-dev-containers` and the **base branch** is the current target (`main` or the active `release/0.X.0` as documented in the release living guide or RELEASE_CHECKLIST.md).
4. Fill out the PR template completely.
5. Link any related issues using `Closes #123` or `Resolves #123`.

Your PR will automatically trigger CI checks (linting via ruff + ShellCheck + actionlint etc., tests via pytest, devcontainer validation where applicable). All checks must pass before review. The branch protection rules on the target (main or the release branch) will also be enforced.

## Commit Message Convention

All commits **must** follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Allowed types** (lowest to highest precedence):
- `fix`, `feat`, `docs`, `refactor`, `test`, `chore`, `build`, `ci`, `perf`, `style`

**Scope examples**: `docker`, `devcontainer`, `payload`, `docs`, `ci`

**Examples**:
```bash
feat(devcontainer): add Node.js 20 support for Payload CMS 3.x
fix(docker): resolve healthcheck race condition in postgres service
docs: update CONTRIBUTING.md with GitHub Free workflow
```

Commit messages are validated automatically by `commitlint` in the CI pipeline.

## Pull Request Guidelines

- One logical change per PR.
- Keep PRs under 500 lines of code (smaller is better).
- Include a clear title using Conventional Commits format.
- Fill out the entire PR template.
- Add tests for new functionality.
- Update documentation when behavior changes.
- Respond to review comments promptly.

Maintainers will merge only after at least one approval and successful CI.

## Reporting Bugs & Requesting Features

1. Search existing issues to avoid duplicates.
2. Open a new issue using the appropriate template.
3. For bugs, provide:
   - Steps to reproduce
   - Expected vs. actual behavior
   - Payload CMS version, Docker version, host OS
   - `docker compose logs` output

## Contributor License Agreement

All contributions are licensed under the Apache License 2.0 (see [LICENSE](LICENSE)). By submitting a pull request, you affirm that you have the right to license your contribution under these terms.

## Recognition

Contributors are recognized in:
- The `CONTRIBUTORS.md` file (updated on merge).
- Release notes.
- The XGIC open-source hall of fame.

## Release Contributions & AI-Assisted Execution (0.2.0 and Beyond)

All release work for 0.2.0+ (MongoDB support, AI-first features, etc.) **must be planned, executed, and documented exactly as if you were a new external contributor**, following the full GitHub Flow + fork/PR model + OSS best practices described in this document, *in addition to* the project's internal guidelines (AGENTS.md, etc.).

This is a deliberate, synergistic requirement:
- Provides **clear, living examples** that future contributors can literally follow or reference.
- Demonstrates deep expertise in professional OSS processes.
- Elevates XGIC's reputation as a thoughtful, AI-first, contributor-friendly open-source leader in the Payload + Dev Containers space.
- Turns internal release work into public goods (the artifacts become onboarding material and proof of quality).

**The process (external contributor simulation + heavy Grok Build AI automation with human gates)**:
- Follow the exact "Step-by-Step Guide: Initiating a New Feature Branch (GitHub Free Account)" above (fork simulation, clone, upstream, feature branch like `feat/0.2.0-mongodb-support`, Conventional Commits, full PR template, etc.).
- Start every implementation/planning session with the AGENTS session startup (`xgic --help; xgic check; xgic payload env`).
- All commits: atomic, full functionality (code + tests + docs), ruff + relevant pytest green, 80-col for code, positive tone, update AGENTS.md, platform issues and primary plan, and playbooks where philosophy changes. Push regularly.
- Grok Build (as the AI-first project) automates as much as possible using its GitHub MCP tools (`create_branch`, `issue_write`/`create_issue`, `create_pull_request` with `draft: true`, `push_files`/`create_or_update_file`, `add_issue_comment`, review tools, etc.) and `run_terminal_command` (gh CLI). 
  - Examples: Grok creates the feat branch, drafts the milestone + labeled "ai-draft" issues for sub-tasks (with bodies that explicitly instruct to follow this process), drafts the PR from the branch, applies file changes, etc.
  - **Mandatory human/developer verification and approval at every gate**: Review the tool output/draft (on GitHub or in session), approve/comment ("LGTM, proceed"), then Grok executes the remote action. Never bypass. Log everything for audit/reputation.
- Use GitHub milestones (e.g., "0.2.0"), Projects, labels, and link everything ("Closes #xxx").
- The full history + a dedicated narrative guide (see `docs/releases/0.2.0-...-external-contributor-guide.md`) becomes the reusable template for 0.3.0+ and a reputation asset.
- Post-merge: Grok can help update "Done" in platform issues and primary plan, CONTRIBUTORS.md, release notes, etc. (with human approval).

See the approved high-level plan in the private session plan.md (and the living 0.2.0 guide) for the detailed vision, high-level scopes (Mongo for 0.2.0; context detection, library extraction, E2E, stage, TUI, etc. for 0.3.0), risks, success criteria, and Grok-specific automation examples. All release work must produce clear examples while advancing the mission of being the #1 agent-optimized foundation for Payload CMS.

This section was added as part of the 0.2.0+ planning (see platform issues and primary plan "Future Releases" and the external simulation requirement). It extends (does not replace) the existing contributor guide.

## For AI Coding Assistants

If you are an AI coding assistant (Grok Build, Claude, Cursor, etc.), please read the following in order **before** making changes:

1. [AGENTS.md](AGENTS.md) — Primary context document (most important)
2. [docs/grok-playbooks.md](docs/grok-playbooks.md) — Concrete workflows and playbooks
3. [docs/architecture.md](docs/architecture.md)
4. Multi-repo standards: https://github.com/xgic/ai (including [ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md))

`AGENTS.md` contains:
- Template consumer model (modular XGIC CLI only)
- How to think and operate effectively as an agent here
- Recommended workflows and command usage
- Safety guidance
- Where CLI implementation work belongs (modular package repos)

**For release work (0.2.0+)**: Additionally follow the "Release Contributions & AI-Assisted Execution" section above + the external contributor simulation in the 0.2.0 living guide. Grok Build will heavily use its GitHub MCP tools for automation (branch, draft issues/PRs with "ai-draft" labels, file pushes, comments) **but every remote action requires explicit human/developer verification and approval before execution**. This is non-negotiable for auditability, correctness, and to demonstrate the AI-first + professional OSS leadership that elevates the project and XGIC.

This project is explicitly designed to become one of the best possible foundations for agentic (Grok Build, etc.) development of Payload CMS applications.

---

**Thank you for helping make Payload CMS development faster, more reliable, and more accessible for the entire community.**

Questions? Open an issue or reach out to the maintainers via Discussions.  
Last updated: [current – added Release Contributions & AI-Assisted Execution section per 0.2.0+ external simulation plan]

## Multi-repo standards

Portfolio standards and community health: https://github.com/xgic/ai (https://github.com/xgic/ai/blob/main/docs/community-health.md).

