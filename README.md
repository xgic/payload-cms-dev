# XGIC Payload CMS Dev

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Payload CMS](https://img.shields.io/badge/Payload%20CMS-3.x+-000000?logo=payloadcms&logoColor=white)](https://payloadcms.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![GHCR](https://img.shields.io/badge/GHCR-payload--cms--dev-blue?logo=github)](https://github.com/users/xgic/packages/container/package/payload-cms-dev)
[![Release](https://img.shields.io/github/v/release/xgic/payload-cms-dev)](https://github.com/xgic/payload-cms-dev/releases)

**Dev Container image producer** for professional [Payload CMS](https://payloadcms.com) development.

This repository builds and publishes the multi-arch image:

```text
ghcr.io/xgic/payload-cms-dev
```

Application teams and AI coding agents consume that image through the thin end-user template:

**→ [xgic/payload-cms](https://github.com/xgic/payload-cms)** (recommended starting point for new Payload projects)

Standards and multi-repo architecture: [xgic/ai](https://github.com/xgic/ai) · [ADR-0001](https://github.com/xgic/ai/blob/main/docs/adr/0001-xgic-gitlab-architecture-and-repository-naming.md) · [ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md)

---

## Why this repository exists

Payload CMS rewards a **reproducible, opinionated environment**: pinned Node/pnpm, a real database, GraphQL-aware tooling, and a single command surface for humans and AI assistants. Shipping that as a **published container image**—not only a Dockerfile in every app repo—gives you:

| Benefit | Outcome |
|---------|---------|
| **Separation of concerns** | Image and CI evolve here; applications start from a thin template |
| **Reproducibility** | Semver tags (`0.3.0`) and multi-arch GHCR delivery |
| **Speed** | App repos pull a pre-built image instead of rebuilding the world |
| **AI-ready operations** | Modular **XGIC CLI** (`xgic`) is installed in the image and documented for agents |
| **Open-source excellence** | Apache-2.0, human-reviewed PRs, public-safe docs, Dependabot, and required CI |

XGIC designs this stack as **production-minded developer infrastructure**: Docker Compose first, configuration over hard-coding, idempotent lifecycle commands, and clear ownership between **producer**, **template**, and **CLI modules**.

---

## Dual-repo model (ADR-0001)

| Repository | Role | You use it when… |
|------------|------|------------------|
| **This repo** — [payload-cms-dev](https://github.com/xgic/payload-cms-dev) | `*-dev` **producer**: Dockerfile, Compose, GHCR publish, infra extensions | You improve the image, CI, or container tooling |
| [payload-cms](https://github.com/xgic/payload-cms) | Clean **end-user template**: thin `devcontainer.json` + app-focused extensions | You **start or develop a Payload application** |

```text
  PyPI: xgic-cli · xgic-dev-cli · xgic-payload-cms-cli
                    │  installed into image
                    ▼
  ┌─────────────────────────────┐     publishes      ┌──────────────────────────┐
  │  xgic/payload-cms-dev       │ ─────────────────► │ ghcr.io/xgic/             │
  │  (this repository)          │                    │   payload-cms-dev         │
  └─────────────────────────────┘                    └────────────┬─────────────┘
                                                                  │ image:
                                                                  ▼
                                                     ┌──────────────────────────┐
                                                     │  xgic/payload-cms        │
                                                     │  (application template)  │
                                                     └──────────────────────────┘
```

**Do not** reintroduce an in-tree CLI package here. Command implementations live in modular packages ([xgic/cli](https://github.com/xgic/cli), [xgic/dev-cli](https://github.com/xgic/dev-cli), [xgic/payload-cms-cli](https://github.com/xgic/payload-cms-cli)).

---

## Features

### Image and runtime

- **Multi-stage Dockerfile** optimized for layer caching (core → system → tools → dev)
- **Node.js LTS Slim** + **pnpm 10** (aligned with modern Payload CMS workflows)
- **Python 3.14** venv with modular **XGIC CLI** from PyPI (version-pinned)
- **Docker Compose** project with optional **PostgreSQL 18** and **MongoDB** profiles
- **Docker-in-Docker** / socket access patterns for container-aware workflows
- Non-root `node` user and workspace-oriented layout
- Multi-arch GHCR publish: **`linux/amd64`** and **`linux/arm64`**

### Developer and AI experience

- **XGIC CLI** on `PATH` for humans and agents (`xgic`, `xgic payload …`)
- Idempotent setup hooks (quiet on re-entry)
- Curated VS Code extensions for Payload, TypeScript, GraphQL, Docker, and SQL
- `create-payload-config.json` + JSON Schema for editor IntelliSense
- CI: Lint, Test, Release Validation, and **Publish GHCR**

### What you get after “Reopen in Container”

A ready workspace with Node, pnpm, database clients, modular `xgic` CLI, and project bootstrap tooling—so contributors and AI agents spend time on **Payload product work**, not environment archaeology.

---

## Pull the published image

```bash
# Rolling producer main
docker pull ghcr.io/xgic/payload-cms-dev:latest

# Reproducible release (recommended for app pins)
docker pull ghcr.io/xgic/payload-cms-dev:0.3.0
```

Package: [ghcr.io/xgic/payload-cms-dev](https://github.com/users/xgic/packages/container/package/payload-cms-dev)  
Releases: [github.com/xgic/payload-cms-dev/releases](https://github.com/xgic/payload-cms-dev/releases)

---

## Start a Payload application (recommended path)

**Most users should not fork this producer repository for application work.**

1. Open **[xgic/payload-cms](https://github.com/xgic/payload-cms)**
2. Use **Use this template** → create your repository  
3. Follow the step-by-step guide in that README (Dev Containers + XGIC CLI)

That template pins a published image and keeps application git history free of image-build noise.

---

## Work on the image / producer (this repository)

Use this repo when you are changing the **container definition**, Compose layout, GHCR pipeline, or producer documentation.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) or Docker Engine  
- [Visual Studio Code](https://code.visualstudio.com/)  
- [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension  

### Getting started (producer workspace)

```bash
git clone https://github.com/xgic/payload-cms-dev.git
cd payload-cms-dev
```

1. Open the folder in VS Code.  
2. **Dev Containers: Reopen in Container** (first open may build locally; several minutes is normal).  
3. Inside the container (explicit CLI — no host Bash lifecycle hooks):

```bash
xgic --version
xgic check
xgic payload env --regenerate --yes   # once: write .devcontainer/.env
xgic payload setup                    # scaffolds under app/ (gitignored)
xgic up --profile postgres            # DB only if not already up via setup
xgic payload dev                      # requires setup first
```

**Layout:** this producer never scaffolds at the workspace root. Generated Payload apps live under **`app/`** (`projectDir` in `.devcontainer/create-payload-config.json`) and are **gitignored**. For real products, use the [payload-cms](https://github.com/xgic/payload-cms) template (app-root layout).

**Git inside the container:** prefer HTTPS + VS Code credential helper. SSH host bind-mounts are not used (Windows `HOME` often empty). A writable named volume is mounted at `~/.ssh` if you install keys manually.

Full command map: [AGENTS.md](AGENTS.md). Architecture notes: [docs/architecture.md](docs/architecture.md).

### Daily XGIC CLI reference (inside the container)

This repository is the **image producer**. Day-to-day **application** work should use the end-user template ([payload-cms](https://github.com/xgic/payload-cms)). The commands below apply when you are **inside a producer Dev Container** (contributing to the image, Compose, or scaffold tooling).

| Command | Purpose |
|---------|---------|
| `xgic --help` / `xgic --version` | Discoverability |
| `xgic check` | Environment / services diagnostic |
| `xgic up` / `xgic down` | Compose lifecycle (`--profile postgres` when needed) |
| `xgic payload env` | Product env status; `--regenerate --yes` for new local secrets |
| `xgic payload dev` | Smart Payload app start (smoke the image like an app workspace) |
| `xgic payload schema` | Regenerate create-payload-config JSON schema after config model changes |
| `xgic payload reset` | Targeted reset for **testing** clean re-scaffold (`--dry-run` first, then `--yes`) |

#### `xgic payload setup` — explicit first-run / validation

Setup is **explicit** (not automatic on Dev Container start). Run it after a fresh workspace, after `xgic payload reset --yes`, when validating `create-payload-config.json`, or in CI-style smoke. Day-to-day work prefers **`xgic payload dev`**, **`xgic check`**, and **`xgic up` / `down`**.

```bash
# First session (or after reset):
xgic payload env --regenerate --yes   # if .devcontainer/.env is missing
xgic payload setup
xgic up --profile postgres
xgic payload dev
# ... contribute to image tooling or smoke the app path ...
xgic down

# Validation after intentional reset:
xgic payload reset --dry-run
xgic payload reset --yes
xgic payload setup
```

### Optional host-side CLI (diagnostics only)

Prefer working **inside** the Dev Container. For host diagnostics, use [uv](https://docs.astral.sh/uv/) and PyPI pins ([python-package-release.md](https://github.com/xgic/ai/blob/main/docs/python-package-release.md)):

```bash
uv venv .venv
# Windows: .venv\Scripts\activate
# Unix:    source .venv/bin/activate
uv pip install \
  "xgic-cli>=0.2.0,<0.3" \
  "xgic-dev-cli>=0.2.0,<0.3" \
  "xgic-payload-cms-cli>=0.2.2,<0.3"
xgic --version
xgic payload --help
```

---

## Pre-configured VS Code extensions (producer)

The producer image/workspace includes tooling for **both** container infrastructure and Payload development:

| Extension | Purpose |
|-----------|---------|
| [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss) | Admin UI / Tailwind workflows |
| [npm IntelliSense](https://marketplace.visualstudio.com/items?itemName=christian-kohler.npm-intellisense) | Package import completion |
| [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) | JS/TS linting |
| [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) | Format on save |
| [GraphQL](https://marketplace.visualstudio.com/items?itemName=GraphQL.vscode-graphql) | Payload GraphQL APIs |
| [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) | Image and Compose editing |
| [TypeScript](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-typescript-next) | Language service |
| [SQLTools + PostgreSQL](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools) | Database exploration |
| [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker) | Docs and code spelling |
| [ErrorLens](https://marketplace.visualstudio.com/items?itemName=usernamehw.errorlens) | Inline diagnostics |

The **application template** keeps a **minimal, app-focused** subset—see [payload-cms](https://github.com/xgic/payload-cms).

---

## Repository structure

```text
.
├── .devcontainer/
│   ├── create-payload-config.json      # Scaffold config (+ JSON Schema)
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   ├── Dockerfile                      # Multi-stage image definition
│   └── scripts/                        # init-env, setup-payload, smoke tests
├── .github/workflows/                  # Lint, Test, Release Validation, Publish GHCR
├── docs/
├── tests/
├── AGENTS.md                           # Agent-first command map and ownership rules
├── CONTRIBUTING.md
├── RELEASE_CHECKLIST.md
└── README.md
```

---

## Working with AI coding assistants

Point assistants at **[AGENTS.md](AGENTS.md)** and prefer **XGIC CLI** for environment operations—not ad-hoc shell recipes.

**Effective prompts**

- “Run `xgic check` and summarize service health.”  
- “Use `xgic payload env` then `xgic payload dev`; report if Postgres is required.”  
- “Show `xgic payload reset --dry-run` blast radius before any destructive reset.”  

**Ownership rules for agents**

| Change type | Land the PR in |
|-------------|----------------|
| Dockerfile, Compose, GHCR, producer CI | **This repository** |
| `xgic` / `xgic payload` behavior | [cli](https://github.com/xgic/cli) / [dev-cli](https://github.com/xgic/dev-cli) / [payload-cms-cli](https://github.com/xgic/payload-cms-cli) |
| App-only template (`devcontainer.json` image pin, app extensions) | [payload-cms](https://github.com/xgic/payload-cms) |

Public GitHub writes must follow the hub **public-safe** gate: [BASE-STANDARDS](https://github.com/xgic/ai/blob/main/docs/BASE-STANDARDS-FOR-ORCHESTRATED-REPOS.md).

---

## Contributing

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md).  
2. Use short-lived branches, Conventional Commits, and **required labels**.  
3. Open a PR; **human UI review** is required before merge to `main` (agents draft; humans approve).  
4. For releases, use [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

### Rebuild the Dev Container (producer only)

- **First open:** Dev Containers: **Reopen in Container**  
- **After Dockerfile / Compose / devcontainer.json changes:** **Rebuild Without Cache and Reopen in Container**  

---

## Multi-repo standards

| Resource | Purpose |
|----------|---------|
| [xgic/ai](https://github.com/xgic/ai) | Portfolio standards hub |
| [BASE-STANDARDS](https://github.com/xgic/ai/blob/main/docs/BASE-STANDARDS-FOR-ORCHESTRATED-REPOS.md) | Public-safe docs, PR process, quality attributes |
| [Community health](https://github.com/xgic/ai/blob/main/docs/community-health.md) | CODEOWNERS, security, contribution norms |
| [Platform overview](https://github.com/xgic/ai/blob/main/docs/platform/overview.md) | Docker Compose–first platform guidance |
| [Ecosystem catalog](https://github.com/xgic/ai/blob/main/docs/ecosystem/catalog.md) | Component map for agents and humans |

---

## License

Copyright 2026 XGIC.  
Licensed under the [Apache License, Version 2.0](LICENSE).  
See [NOTICE](NOTICE).

---

**XGIC** — Principal architecture for open-source developer platforms: modular CLI, dual-repo Dev Containers, and AI-operable workflows built for long-horizon maintainability.
