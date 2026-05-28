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
| [GitLab Workflow](https://marketplace.visualstudio.com/items?itemName=gitlab.gitlab-workflow)                   | GitLab CI/CD integration and pipeline management                                                             |
| [GraphQL](https://marketplace.visualstudio.com/items?itemName=GraphQL.vscode-graphql)                           | Syntax highlighting, validation, and IntelliSense for GraphQL (core to Payload CMS API)                      |
| [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)                       | Dockerfile, Docker Compose, and container management tools                                                   |
| [TypeScript](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-typescript-next)              | Latest TypeScript language features and IntelliSense                                                         |
| [SQLTools + PostgreSQL](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools)                      | Advanced database exploration, querying, and management for PostgreSQL                                       |
| [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker) | Spelling validation across code and documentation                                                            |
| [ErrorLens](https://marketplace.visualstudio.com/items?itemName=usernamehw.errorlens)                           | Inline error and warning annotations for improved visibility                                                 |

These extensions ensure a **consistent, high-productivity development environment** right out of the box.

## Quick Start

1. **Clone or use this repository as a GitHub Template**
2. **(Recommended) Install `xde` on your host** for powerful host-side commands before opening the container:
   ```bash
   pipx install -e .   # or: pip install -e . --user
   ```
   This makes `xde dev`, `xde reset`, `xde check`, etc. available immediately on the host.
3. Open the folder in **VS Code**
4. Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> then select the **Dev Containers: Rebuild Without Cache and Reopen in Container** option.
5. The development container's `initializeCommand` will automatically generate your secure `.env` file (PostgreSQL credentials)
6. The container lifecycle will:
   - Run `initializeCommand` to generate `.env`
   - Run `postStartCommand` which executes `setup-payload.sh` (idempotent project creation)
7. After creation completes, run `pnpm dev` in the new Payload subdirectory
8. Open http://localhost:3000/admin

**Payload Creation Flow**

The real work happens in `.devcontainer/scripts/setup-payload.sh`, which is:
- Called automatically via `postStartCommand` when the dev container starts
- Idempotent — safe to run multiple times

**For non-interactive / CI/CD automation** (e.g., when using this repo as a template):
- Customize `.devcontainer/create-payload-config.json` with supported parameters.
- The file has full JSON Schema support → excellent VS Code IntelliSense, validation, and autocomplete out of the box.
- See `.devcontainer/create-payload-config.schema.json` for the complete schema.

Happy coding your dream web apps using Payload CMS in our optimized development environment.

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
| `xde dev`                | **Primary daily command.** Starts the Payload development server. Performs a DB readiness check first. If containers are not running, prints a clear, actionable prompt instead of a raw error. |
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

During active development of the `xde` CLI, the recommended way to use it on the host is via an editable install (see the Quick Start section above). A proper console script entry point is provided by the `pyproject.toml`.

## Working with AI Assistants (Grok, etc.)

Ask AI tools to use the `xde` CLI for environment operations. Example prompts:

- "Run `xde dev` and tell me if the database is ready."
- "Use `xde reset --yes` then start the dev server."
- "Run `xde validate` and summarize any issues."

During the transition period some legacy automation targets may still exist for compatibility, but the canonical interface is `xde`.

## Next Steps

- Review [CONTRIBUTING.md](.github/CONTRIBUTING.md) — start with the [Code Style Quick Reference](.github/CONTRIBUTING.md#code-style-quick-reference).
- **AI assistants**: Read [AGENTS.md](AGENTS.md) first for project-specific guidance.
- The `xde` CLI source and full documentation live alongside this README (implementation in progress).

## License

MIT © 2026 [XGIC](https://xgic.net). See [LICENSE](LICENSE) file for details.

---

**Made with expertise by XGIC** — Demonstrating world-class software architecture, DevOps excellence, and superior developer experience.
