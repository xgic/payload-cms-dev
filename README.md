# XGIC Payload CMS VS Code Dev Containers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Payload CMS](https://img.shields.io/badge/Payload%20CMS-3.x+-000000?logo=payloadcms&logoColor=white)](https://payloadcms.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

> **Official XGIC template** — Rapid, reproducible, production-grade Payload CMS development environment using VS Code **Dev Containers** + **Docker Compose** + **PostgreSQL 18** + **automated project creation**.

## Features

- **Node.js LTS Slim** + **pnpm 10** (pinned for maximum Payload CMS compatibility)
- **PostgreSQL 18** server + client with persistent data volume
- Docker-in-Docker + Buildx + Compose support
- Non-root `node` user and security-hardened base image
- Automated environment validation via `devcontainer-tests.sh`
- Automated/semi-automated Payload CMS project creation during devcontainer startup

### Pre-configured VS Code Extensions

This template comes with a **carefully curated set of VS Code extensions** pre-installed via `.devcontainer/devcontainer.json`. These extensions provide a fully optimized, zero-configuration development experience for Payload CMS projects. Developers can start coding immediately without manually installing or configuring tools.

| Extension                                                                                                       | Purpose                                                                                                      |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)      | Intelligent autocomplete, linting, and hover previews for Tailwind CSS (widely used in Payload admin panels) |
| [npm IntelliSense](https://marketplace.visualstudio.com/items?itemName=christian-kohler.npm-intellisense)       | Enhanced autocompletion for npm and pnpm packages                                                            |
| [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)                            | Real-time JavaScript/TypeScript linting and error detection                                                  |
| [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)                          | Consistent code formatting on save (default formatter)                                                       |
| [GraphQL](https://marketplace.visualstudio.com/items?itemName=GraphQL.vscode-graphql)                           | Syntax highlighting, validation, and IntelliSense for GraphQL (core to Payload CMS API)                      |
| [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)                       | Dockerfile, Docker Compose, and container management tools                                                   |
| [TypeScript](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-typescript-next)              | Latest TypeScript language features and IntelliSense                                                         |
| [SQLTools + PostgreSQL](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools)                      | Advanced database exploration, querying, and management for PostgreSQL                                       |
| [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker) | Spelling validation across code and documentation                                                            |
| [ErrorLens](https://marketplace.visualstudio.com/items?itemName=usernamehw.errorlens)                           | Inline error and warning annotations for improved visibility                                                 |

These extensions ensure a **consistent, high-productivity development environment** right out of the box.

## Quick Start

This repository includes a [VS Code Dev Container](https://code.visualstudio.com/docs/devcontainers/containers) configuration that provides a consistent, fully provisioned development environment for Payload CMS projects.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows/macOS) or Docker Engine (Linux)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension for VS Code

### Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/XGIC/payload-cms-dev-containers.git
   cd payload-cms-dev-containers
   ```

2. Open the folder in Visual Studio Code.

3. When prompted, select **Reopen in Container** (or run **Dev Containers: Reopen in Container** from the Command Palette).

   This is the recommended command for the initial container setup.

The container will build on first use (this may take several minutes). Once ready, you will have a pre-configured environment with Node.js, pnpm, recommended VS Code extensions, and Payload CMS development tools already set up. The `xde` CLI is pre-installed and available in your PATH inside the container.

**What to expect during first container creation**
VS Code will show "Running the initializeCommand..." and "Running the postStartCommand..." headers (these come from the Dev Containers extension whenever hooks are defined in devcontainer.json). Our scripts are intentionally minimal and silent on repeat runs (idempotent). The `postCreateCommand` hook has been removed (xde install is baked into the image) to avoid the "Running the postCreateCommand..." header and the "Done. Press any key to close the terminal." prompt. A one-time pnpm "build scripts" warning for a dependency is suppressed via `pnpm approve-builds` during setup.

For full details on how Dev Containers work, see the official documentation:

- [Developing inside a Container](https://code.visualstudio.com/docs/devcontainers/containers)
- [Dev Container Specification](https://containers.dev/)

This configuration is also compatible with GitHub Codespaces.

## Repository Structure

```
.
├── .devcontainer/
│   ├── .env                           # Dynamically generated (never commit)
│   ├── create-payload-config.json     # ← Main config (has JSON Schema for great VS Code IntelliSense)
│   ├── create-payload-config.schema.json
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── scripts/
│       ├── setup-payload.sh            # Main project creation logic (postStartCommand)
│       ├── devcontainer-tests.sh
│       ├── init-env.sh
│       └── reset-project.py              # Reliable Python implementation of fast environment resets
├── .dockerignore
├── .github/
│   └── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Architecture

- Multi-stage **Dockerfile** (core → dev_tools → dev)
- Docker Compose orchestration for app + postgres services
- Isolated bridge network + named volumes for data persistence
- Delegated bind mounts for optimal performance

## The `xde` CLI

`xde` (XGIC Dev Environment) is the primary command-line tool for managing the development environment. It provides a reliable, testable, and developer-friendly replacement for the previous automation targets.

**AI coding assistants** (Grok Build, Claude, Cursor, etc.): 

**Start here** (in this order for maximum effectiveness):
1. [AGENTS.md](AGENTS.md) — Primary behavioral and philosophical guidance.
2. [docs/grok-playbooks.md](docs/grok-playbooks.md) — Concrete step-by-step workflows and playbooks.
3. [GROK-TASKS.md](GROK-TASKS.md) — Lightweight task tracking for informal TODOs and reminders.
4. [DEV-JOURNAL.md](DEV-JOURNAL.md) — History of our collaboration and major decisions.
5. [docs/architecture.md](docs/architecture.md) — Mental model.
6. [docs/xde-reference.md](docs/xde-reference.md) — Command surface details.

These documents are deliberately written to make Grok Build (and similar agents) dramatically more productive when working on Payload CMS projects with this template.

All commands are designed to feel natural when working inside the Dev Container (the default context is development). The only explicit non-development environment is `stage` (for testing code that mirrors production).

### Quick Reference

| Command                  | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `xde` or `xde help`      | Show short, scannable usage information (level-1 help).                     |
| `xde dev`                | **Primary daily command.** Starts the Payload development server (direct inside container for clean Ctrl+C handling; Docker only for cross-service or host orchestration). Performs a DB readiness check first. |
| `xde up`                 | Start all development services (Docker Compose).                            |
| `xde down`               | Stop containers (volumes are preserved).                                    |
| `xde reset`              | Fast targeted reset: removes the generated Payload project folder and resets the Postgres data volume (stable credentials). |
| `xde check`              | Diagnostic: verify that PostgreSQL and required services are reachable.     |
| `xde logs`               | Follow logs for all services.                                               |
| `xde shell`              | Open an interactive shell in the main service container.                    |

### Planned Extensions (Post v1)

The following capabilities are under consideration for future releases:

- **Staging-Mirror Testing**: A `stage` namespace for testing against production-like environments (e.g., `xde stage up`).
- **Maintenance & Quality commands**: `xde validate`, `xde lint`, `xde schema`.
- **Interactive Experience**: A Textual-based TUI (`xde tui`) for dashboards, logs, and wizards.

These features are not part of the initial v1 command surface.

### Usage Examples

```bash
# Start developing (recommended)
xde dev

# Full environment lifecycle
xde up
# ... work ...
xde down

# Safe reset before a fresh test run
xde reset --yes

# Test against a production-like database and services
xde stage up
xde stage dev
```

### Development Note

The `xde` CLI is installed by default inside the Dev Container (the primary environment where the vast majority of development work happens). You do not need to install anything extra on your host for normal daily use.

If you are actively developing the `xde` CLI itself, or need the commands on the host before the container is running (advanced / power-user scenarios), see the "Advanced: Installing xde on the Host (Optional)" section below. A proper console script entry point is provided by the `pyproject.toml`.

## Advanced: Installing xde on the Host (Optional)

The `xde` CLI is pre-installed and available inside the Dev Container by default (via the container's Python venv and postCreateCommand). This is the recommended and primary experience — users do most of their work inside the container.

Host installation is entirely optional and intended only for advanced / power-user cases such as:
- Running `xde check`, `xde env`, or `xde reset` from the host *before* the container is open.
- Host-only scripting or CI that cannot easily use the dev container.
- Actively developing changes to the xde source code on the host machine.
- Using xde in environments outside a dev container (e.g., certain GitHub Actions runners).

**Recommended modern tooling: uv**

We prefer `uv tool install -e .` (from Astral) for isolated, fast, editable tool installs. It is actively maintained and generally faster than older alternatives.

**macOS and Linux**

```bash
# One-time setup: install uv (if you do not already have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# From the root of this repository:
uv tool install -e .
```

After installation, the `xde` command should be available in your shell (you may need to open a new terminal or ensure `~/.local/bin` is on your PATH — uv usually configures this for you).

**Windows (PowerShell)**

```powershell
# One-time setup: install uv (if you do not already have it)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# From the root of this repository (in PowerShell):
uv tool install -e .
```

**Platform notes and caveats**
- Editable installs (`-e`) mean that local changes to the xde source are reflected immediately when you run `xde` (very useful when developing the CLI).
- PATH differences: The exact location uv places tools varies by platform and shell. Common locations include `~/.local/bin` (Unix) or the uv tools directory on Windows. Restart your terminal after install if `xde` is not found.
- To upgrade a tool install: `uv tool upgrade xde`
- To remove: `uv tool uninstall xde`
- This section is deliberately separated from the main Quick Start because most users (and all first-time container users) never need it.

## Working with AI Assistants (Grok, etc.)

Ask AI tools to use the `xde` CLI for environment operations. Example prompts:

- "Run `xde dev` and tell me if the database is ready."
- "Use `xde reset --yes` then start the dev server."
- "Run `xde validate` and summarize any issues."

During the transition period some legacy automation targets may still exist for compatibility, but the canonical interface is `xde`.

## Troubleshooting

### Rebuilding or Updating the Development Container

For the **initial setup**, always use **Dev Containers: Reopen in Container** (as shown in the Quick Start above).

**Rebuild Without Cache and Reopen in Container** should only be used when:

- You have modified container configuration files (`Dockerfile`, `devcontainer.json`, `docker-compose.yml`, etc.)
- You need to force a clean image rebuild (e.g., after dependency changes in the container or to troubleshoot build issues)
- The container is in a broken state

To trigger a full rebuild:

1. Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> (or <kbd>Cmd</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> on macOS)
2. Select **Dev Containers: Rebuild Without Cache and Reopen in Container**

This will discard cached layers and recreate the container from scratch.

## Next Steps

- Review [CONTRIBUTING.md](.github/CONTRIBUTING.md) — start with the [Code Style Quick Reference](.github/CONTRIBUTING.md#code-style-quick-reference).
- **AI assistants**: Read [AGENTS.md](AGENTS.md) first for project-specific guidance.
- The `xde` CLI source and full documentation live alongside this README (implementation in progress).

## License

MIT © 2026 [XGIC](https://xgic.net). See [LICENSE](LICENSE) file for details.

---

**Made with expertise by XGIC** — Demonstrating world-class software architecture, DevOps excellence, and superior developer experience.
