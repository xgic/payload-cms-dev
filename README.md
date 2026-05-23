# XGIC Payload CMS VS Code Dev Containers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Payload CMS](https://img.shields.io/badge/Payload%20CMS-3.x+-000000?logo=payloadcms&logoColor=white)](https://payloadcms.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

> **Official XGIC template** — Rapid, reproducible, production-grade Payload CMS development environment using VS Code **Dev Containers** + **Docker Compose** + **PostgreSQL 18** + **pgAdmin**.

## Features

- **Node.js LTS Slim** + **pnpm 10** (pinned for maximum Payload CMS compatibility)
- **PostgreSQL 18** server + client with persistent data volume
- **pgAdmin 4** pre-configured (accessible on port 8080)
- Docker-in-Docker + Buildx + Compose support
- Non-root `node` user and security-hardened base image
- Automated environment validation via `devcontainer-tests.sh`
- Ready for `create-payload-app@latest`

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
4. The development container's `initializeCommand` will automatically generate your secure `.env` file (PostgreSQL + pgAdmin credentials)
5. The `postCreateCommand` will:
   - Run environment validation (`devcontainer-tests.sh`)
   - **Launch the official Payload CMS interactive wizard** (`pnpx create-payload-app@latest`)
6. When prompted by the wizard, choose your template (website, blank, etc.) and project name
7. After the wizard completes, run `pnpm dev` in the new Payload subdirectory
8. Open http://localhost:3000/admin and http://localhost:8080 (pgAdmin)

**For non-interactive / CI/CD automation** (e.g., when using this repo as a template):
- Customize `.devcontainer/create-payload-config.json` with all supported parameters (see [official Payload CMS documentation](https://payloadcms.com/docs/getting-started/installation) for additional information):
  - projectName → directory name (positional argument)
  - template → blank | website | ecommerce | custom (official templates)
  - yes → --yes flag (skip all prompts)
  - typescript → TypeScript vs JavaScript
  - dbAdapter / dbUri → Database configuration
  - adminEmail / adminPassword → Initial admin user
  - plugins / example → Additional options
- The wizard will be skipped and the Payload CMS project will be created automatically.

   Happy codding your dream web apps using Payload CMS in our optimized development environment.

## Repository Structure

```
.
├── .devcontainer/
│   ├── .env                  # Dynamically generated (never commit for security)
│   ├── create-payload-config.json
│   ├── devcontainer-tests.sh
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── init-env.sh
│   └── post-create.sh
├── .dockerignore
├── .github/              # CI, CODE_OF_CONDUCT, etc.
│   └──  CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Architecture

- Multi-stage **Dockerfile** (core → dev_tools → dev)
- Docker Compose orchestration for app + postgres + pgadmin services
- Isolated bridge network + named volumes for data persistence
- Delegated bind mounts for optimal performance

## Next Steps

- Review [CONTRIBUTING.md](.github/CONTRIBUTING.md)
- See full documentation in the `docs/` folder (coming soon)

## License

MIT © 2026 [XGIC](https://xgic.net). See [LICENSE](LICENSE) file for details.

---

**Made with expertise by XGIC** — Demonstrating world-class software architecture, DevOps excellence, and superior developer experience.
