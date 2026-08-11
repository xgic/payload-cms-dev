# XGIC Payload CMS Dev Container (producer)


## Repository role

This repository is the **Dev Container image producer** (`*-dev`, [ADR-0001](https://github.com/xgic/ai/blob/main/docs/adr/0001-xgic-gitlab-architecture-and-repository-naming.md)).

- **Image:** `ghcr.io/xgic/payload-cms-dev` (published on `main` / `v*` via **Publish GHCR** workflow)
- **End-user template:** [xgic/payload-cms](https://github.com/xgic/payload-cms) (consumes the published image)
- **CLI packages:** modular XGIC CLI from PyPI ([ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md))

Formerly published as `payload-cms-dev-containers` (GitHub redirects from the old name).

### Pull the published image

```bash
docker pull ghcr.io/xgic/payload-cms-dev:latest
# Prefer a semver tag after a release: ghcr.io/xgic/payload-cms-dev:0.3.0
```

Package visibility may require a GitHub login for private packages; public packages pull anonymously once published.


[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Payload CMS](https://img.shields.io/badge/Payload%20CMS-3.x+-000000?logo=payloadcms&logoColor=white)](https://payloadcms.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

> **Official XGIC template** — Rapid, reproducible, production-grade Payload CMS development environment using VS Code **Dev Containers** + **Docker Compose** + **PostgreSQL 18** + **automated project creation**.

## Features

- **Node.js LTS Slim** + **pnpm 10** (pinned for maximum Payload CMS compatibility)
- **PostgreSQL 18** server + client with persistent data volume
- Docker-in-Docker + Buildx + Docker Compose support
- Non-root `node` user and security-hardened VS Code Dev Container image
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
   git clone https://github.com/xgic/payload-cms-dev.git
   cd payload-cms-dev
   ```

2. Open the folder in Visual Studio Code.

3. When prompted, select **Reopen in Container** (or run **Dev Containers: Reopen in Container** from the Command Palette).

   This is the recommended command for the initial container setup.

The container will build on first use (this may take several minutes). Once ready, you will have a pre-configured environment with Node.js, pnpm, recommended VS Code extensions, and Payload CMS development tools already set up. The modular **XGIC CLI** (`xgic`) is pre-installed and available on your PATH inside the container.

**Daily commands (inside the container)**

```bash
xgic check
xgic payload env
xgic payload dev
```

See [AGENTS.md](AGENTS.md) for the full command map. Lifecycle helpers: `xgic up` / `xgic down` / `xgic payload reset`.

**What to expect during first container creation**
VS Code will show "Running the initializeCommand..." and "Running the postStartCommand..." headers (these come from the Dev Containers extension whenever hooks are defined in devcontainer.json). Our scripts are intentionally minimal and silent on repeat runs (idempotent). Modular XGIC CLI packages are installed at image build time. A one-time pnpm "build scripts" warning for a dependency is suppressed via `pnpm approve-builds` during setup.

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
│       └── init-env.sh
├── .dockerignore
├── .github/
├── LICENSE
├── AGENTS.md
└── README.md
```

CLI implementation lives in modular public packages ([xgic/cli](https://github.com/xgic/cli), [xgic/dev-cli](https://github.com/xgic/dev-cli), [xgic/payload-cms-cli](https://github.com/xgic/payload-cms-cli)) — this template is a **consumer** only ([ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md)).

## Architecture

- Multi-stage **Dockerfile** (core → dev_tools → dev)
- Docker Compose orchestration for app + postgres services
- Isolated bridge network + named volumes for data persistence
- Delegated bind mounts for optimal performance
- Modular **XGIC CLI** installed into the image Python venv

## XGIC CLI (primary interface)

**Brand:** XGIC CLI (`xgic`). Living docs use this brand only (no supported dual brand).

**AI coding assistants:** start with [AGENTS.md](AGENTS.md), then [docs/architecture.md](docs/architecture.md) and multi-repo standards at [xgic/ai](https://github.com/xgic/ai).

### Quick reference

| Command | Description |
|---------|-------------|
| `xgic --help` | Top-level help |
| `xgic payload dev` | **Primary daily command** — smart Payload CMS app start |
| `xgic up` / `xgic down` | Docker Compose lifecycle (use `--profile postgres` when needed) |
| `xgic check` | Environment / services diagnostic |
| `xgic payload env` | Payload CMS env status; `--regenerate --yes` for new secrets |
| `xgic payload setup` | Ensure project directory (also run by postStart) |
| `xgic payload schema` | Regenerate create-payload-config JSON schema |
| `xgic payload reset` | Targeted reset: project folder + DB volume (`--dry-run` / `--yes`) |

### Usage examples

```bash
xgic payload dev

xgic up --profile postgres
# ... work ...
xgic down

xgic payload reset --dry-run
xgic payload reset --yes
```

### Optional host install

Prefer working **inside** the Dev Container. For host-side diagnostics, install the modular packages from **PyPI** with [uv](https://docs.astral.sh/uv/) (see [python-package-release.md](https://github.com/xgic/ai/blob/main/docs/python-package-release.md)):

```bash
# One-time: install uv if needed — https://docs.astral.sh/uv/getting-started/installation/
uv venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install \
  "xgic-cli>=0.2.0,<0.3" \
  "xgic-dev-cli>=0.2.0,<0.3" \
  "xgic-payload-cms-cli>=0.2.0,<0.3"
xgic --version
xgic payload --help
```

CLI source changes belong in the modular repositories—not in this template.

## Working with AI assistants

Ask tools to use **XGIC CLI** (`xgic` / `xgic payload …`) for environment operations. Example prompts:

- "Run `xgic payload dev` and tell me if the database is ready."
- "Use `xgic payload reset --dry-run` then `--yes` if the plan looks safe."
- "Run `xgic check` and summarize any issues."

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

- Review [CONTRIBUTING.md](CONTRIBUTING.md) — start with the [Code Style Quick Reference](CONTRIBUTING.md#code-style-quick-reference).
- **AI assistants**: Read [AGENTS.md](AGENTS.md) first for project-specific guidance.
- CLI implementation: modular packages ([xgic/cli](https://github.com/xgic/cli), [xgic/dev-cli](https://github.com/xgic/dev-cli), [xgic/payload-cms-cli](https://github.com/xgic/payload-cms-cli)) — this template is a **consumer** only.


## Multi-repo standards

Portfolio standards, ADRs, and community health:

- https://github.com/xgic/ai
- [Community health](https://github.com/xgic/ai/blob/main/docs/community-health.md)
- [BASE-STANDARDS](https://github.com/xgic/ai/blob/main/docs/BASE-STANDARDS-FOR-ORCHESTRATED-REPOS.md)
- [Platform overview (Docker Compose first)](https://github.com/xgic/ai/blob/main/docs/platform/overview.md)

## License

Copyright 2026 XGIC.  
Licensed under the [Apache License, Version 2.0](LICENSE).  
See [NOTICE](NOTICE).


---

**Made with expertise by XGIC** — Demonstrating world-class software architecture, DevOps excellence, and superior developer experience.
