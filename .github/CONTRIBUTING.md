# Contributing to `payload-cms-dev-containers`

**Project**: [XGIC/payload-cms-dev-containers](https://github.com/XGIC/payload-cms-dev-containers)  
**Purpose**: A production-grade, open-source toolkit that enables the rapid creation and setup of highly optimized **Payload CMS** development environments using **Visual Studio Code Dev Containers** orchestrated via **Docker Compose**.  

We welcome contributions from the open-source community. Whether you are fixing a bug, adding support for a new Payload CMS version, improving Docker performance, enhancing documentation, or proposing architectural improvements, your work directly advances developer productivity across the Payload CMS ecosystem.

By participating, you agree to abide by our [Code of Conduct](#code-of-conduct) and the [Contributor License Agreement](#contributor-license-agreement) (implicitly accepted upon submission of a pull request).

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Environment Setup](#development-environment-setup)
- [GitHub Flow & Branching Strategy](#github-flow--branching-strategy)
- [Step-by-Step Guide: Initiating a New Feature Branch (GitHub Free Account)](#step-by-step-guide-initiating-a-new-feature-branch-github-free-account)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Reporting Bugs & Requesting Features](#reporting-bugs--requesting-features)
- [Contributor License Agreement](#contributor-license-agreement)
- [Recognition](#recognition)

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

### Repository Focus
Contributions to this repo typically involve:
- Dockerfiles and Docker Compose files
- Shell scripts (Bash)
- Python automation scripts (especially `create-payload-automated.py`)
- Makefiles
- YAML configuration (Dev Container, GitHub Actions, Dependabot)
- Documentation (README, CONTRIBUTING, etc.)

### Required Standards

- **Dev Containers**: All development work should be done inside the provided Dev Container when possible. Changes must be tested inside the container before opening a PR.
- **Docker**: Follow official [Docker Best Practices](https://docs.docker.com/build/building/best-practices/). Prefer multi-stage builds and minimize image size where reasonable.
- **Shell Scripts**:
  - All `.sh` files must pass `shellcheck` (`make lint-shell`).
  - Prefer POSIX-compliant syntax when practical. Use `set -euo pipefail` (or `set -e`) appropriately.
  - Scripts in `.devcontainer/scripts/` should remain thin orchestration layers where possible. Complex logic belongs in Python (`create-payload-automated.py`).
- **Python**: Follow PEP 8 with type hints where it improves clarity. Keep the automation script (`create-payload-automated.py`) well-documented and focused on the pexpect-driven workflow.
- **YAML & GitHub Actions**: Use consistent indentation (2 spaces). Validate workflows with `actionlint` when making changes to `.github/workflows/`.
- **Documentation**: 
  - Update `README.md` when user-facing behavior changes.
  - Update this file (`CONTRIBUTING.md`) when contribution processes or standards change.
  - Add usage examples for new `make` targets or automation features.

### Recommended Practices
- Keep the thin bash wrappers (`setup-payload.sh`, etc.) minimal. Move logic into the Python automation script when it grows complex.
- Prefer configuration via `create-payload-config.json` over hardcoding values in scripts.
- Test changes using available `make` targets (especially `make lint-shell`, `make post-create`, and `make rebuild`).

All contributors are expected to review this document before submitting code.

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

### Local Development Commands

After entering the Dev Container, the following `make` targets are particularly useful:

| Command            | Purpose                                      |
|--------------------|----------------------------------------------|
| `make help`        | Show all available targets                   |
| `make lint-shell`  | Run shellcheck on all scripts                |
| `make post-create` | Simulate the full Payload creation flow      |
| `make rebuild`     | Clean + rebuild + test the entire environment|
| `make env`         | Show status of the generated `.env` file     |

### Debugging & Logging

You can control the verbosity of the setup scripts using the `LOG_LEVEL` environment variable.

Supported values (case-insensitive):
- `DEBUG` — Most verbose (shows debug messages)
- `INFO` — Default level
- `WARN` (or `WARNING`) — Warnings and errors only
- `ERROR` — Errors only

Examples inside the Dev Container:

```bash
# Run the full setup with maximum verbosity
LOG_LEVEL=DEBUG make exec CMD="bash .devcontainer/scripts/setup-payload.sh"

# Run the Python automation with debug logging
LOG_LEVEL=debug python3 .devcontainer/scripts/create-payload-automated.py --config .devcontainer/create-payload-config.json

# Only show warnings and errors from init-env
LOG_LEVEL=warn bash .devcontainer/scripts/init-env.sh
```

The Python automation script (`create-payload-automated.py`) also respects `LOG_LEVEL`.

This is particularly useful when debugging issues with the automated Payload project creation.

### Contributing to the Automation Logic

The core of the automated Payload CMS project creation lives in `.devcontainer/scripts/create-payload-automated.py` (using `pexpect`).

When working in this area:
- Prefer extending `create-payload-config.json` support over hardcoding behavior.
- Keep the bash scripts in `.devcontainer/scripts/` as thin, readable wrappers.
- Test changes locally with `make post-create` or by invoking the Python script directly inside the Dev Container.
- Update relevant documentation (README, script help text) when user-visible behavior changes.

### Linting & Quality

This repository uses several tools to maintain code quality:

- **Shell scripts**: `shellcheck` (`make lint-shell`). `shellcheck` is pre-installed in the Dev Container.
- **GitHub Actions workflows**: `actionlint` (run via CI).
- **Shell formatting**: `shfmt` (enforced in CI).

The full lint suite runs automatically on every pull request (see `.github/workflows/lint.yml`). You can run the main shell linter locally with:

```bash
make lint-shell
```

## GitHub Flow & Branching Strategy

We follow the **GitHub Flow** model:
- The `main` branch is the only long-lived branch and is always in a releasable state.
- All changes are made in short-lived **feature branches** created from `main`.
- Every pull request targets `main`.
- Protected branch rules (enforced via repository settings) require passing status checks and at least one approving review before merging.

**Branch naming convention** (enforced via Conventional Commits tooling):
- `feat/...` – new features or enhancements
- `fix/...` – bug fixes
- `docs/...` – documentation changes
- `refactor/...` – code refactoring without functional change
- `test/...` – adding or updating tests
- `chore/...` – build, CI, or tooling changes

## Step-by-Step Guide: Initiating a New Feature Branch (GitHub Free Account)

GitHub Free accounts do **not** grant direct push access to organization repositories. Therefore, all external contributors **must** use the **Fork + Pull Request** workflow. The following guide is tailored specifically for contributors to `XGIC/payload-cms-dev-containers` and adheres to GitHub’s official best practices (GitHub Flow, fork model, and Conventional Commits).

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
Always start from the latest `main`:
```bash
git fetch upstream
git checkout main
git merge upstream/main   # or git rebase upstream/main
git push origin main
```

### Step 5: Create a New Feature Branch
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
- Keep changes small, focused, and atomic.

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
3. Ensure the base repository is `XGIC/payload-cms-dev-containers` and base branch is `main`.
4. Fill out the PR template completely.
5. Link any related issues using `Closes #123` or `Resolves #123`.

Your PR will automatically trigger CI checks (Docker build, linting, tests). All checks must pass before review.

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

All contributions are licensed under the project’s [MIT License](LICENSE). By submitting a pull request, you affirm that you have the right to license your contribution under these terms.

## Recognition

Contributors are recognized in:
- The `CONTRIBUTORS.md` file (updated on merge).
- Release notes.
- The XGIC open-source hall of fame.

---

**Thank you for helping make Payload CMS development faster, more reliable, and more accessible for the entire community.**

Questions? Open an issue or reach out to the maintainers via Discussions.  
Last updated: June 2026