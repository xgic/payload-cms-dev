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
2. Open the folder in **VS Code**
3. Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> then select the **Dev Containers: Rebuild Without Cache and Reopen in Container** option.
4. The development container's `initializeCommand` will automatically generate your secure `.env` file (PostgreSQL credentials)
5. The container lifecycle will:
   - Run `initializeCommand` to generate `.env`
   - Run `postStartCommand` which executes `setup-payload.sh` (idempotent project creation)
6. After creation completes, run `pnpm dev` in the new Payload subdirectory
7. Open http://localhost:3000/admin

**For non-interactive / CI/CD automation** (e.g., when using this repo as a template):
- Customize `.devcontainer/create-payload-config.json` with supported parameters (projectName, template, dbAdapter, dbUri, etc.).
- Project creation is handled by `.devcontainer/scripts/setup-payload.sh` (invoked via `postStartCommand`).

   Happy coding your dream web apps using Payload CMS in our optimized development environment.

## Repository Structure

```
.
├── .devcontainer/
│   ├── .env                      # Dynamically generated (never commit)
│   ├── create-payload-config.json
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── scripts/
│       ├── setup-payload.sh            # Main project creation logic (postStartCommand)
│       ├── devcontainer-tests.sh
│       ├── init-env.sh
│       ├── post-create.sh                # Legacy compatibility shim (deprecated)
│       └── reset-project.py              # Python implementation of make reset-project
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

## Working with AI Assistants (Grok, etc.)

This repository is designed to work well with AI coding assistants. When asking an AI (such as Grok) to run commands:

- **Default behavior**: Ask it to run commands **inside the Dev Container** using `make exec`, `make python`, or `make test-in-container`.
- Example prompts:
  - "Run `make validate` inside the container"
  - "Execute the automation script with `--dry-run` using the container"
  - "Run pytest on the new tests inside the dev container"

Convenience targets exist in the Makefile:
- `make exec CMD="..."` — Run any command inside the container as the `node` user.
- `make python CMD="..."` — Run Python (from the venv) inside the container.
- `make test-in-container` — Run pytest inside the container.

This keeps the AI's environment consistent with actual development.

## Next Steps

- Review [CONTRIBUTING.md](.github/CONTRIBUTING.md) (includes development setup and linting instructions)
- See full documentation in the `docs/` folder (coming soon)

## License

MIT © 2026 [XGIC](https://xgic.net). See [LICENSE](LICENSE) file for details.

---

**Made with expertise by XGIC** — Demonstrating world-class software architecture, DevOps excellence, and superior developer experience.
