# Architecture Overview

This document gives AI agents (especially Grok Build) a clear mental model of the system.

## High-Level Layers

1. **Host Machine**
   - Where the developer (and sometimes the agent) runs `xde` commands directly.
   - Can perform host-only operations (Docker Compose control, file system changes to the generated Payload project, etc.).

2. **Dev Container** (the primary development environment)
   - Runs as the `node` user.
   - Has the full Payload project mounted at `/workspace/<projectName>`.
   - Contains the generated Payload app + its dependencies.
   - PostgreSQL runs as a sibling container on an isolated network.

3. **xde CLI** (`src/xde/`)
   - The **strategic direction** of the project.
   - Single, clean, testable interface for all environment operations.
   - Designed to be excellent for both humans and agents.

4. **Legacy Automation** (being migrated)
   - `Makefile`
   - `.devcontainer/scripts/*.sh` and `*.py`
   - These exist for backward compatibility during the transition.

## Core Abstractions (Most Important for Agents)

### EnvironmentContext (`src/xde/core/environment.py`)

Tells you where you are running:
- `HOST`
- `DEV_CONTAINER`
- `GENERIC_CONTAINER`

This replaces the old fragile Makefile `HOST_ONLY_GUARD` / `RUN_IN_CONTAINER` macros.

**Always** start by understanding the environment context when reasoning about a task.

### DockerComposeController (`src/xde/core/docker.py`)

The single place that talks to Docker Compose.

Current responsibilities:
- Start/stop/build services
- Query service status
- Execute commands inside containers

Future responsibilities:
- Better status parsing
- Streaming logs
- Health checks

### Configuration System

- `create-payload-config.json` + JSON Schema = **single source of truth** for how a new Payload project should be generated.
- `types.ts` (in `.devcontainer/config/`) is the TypeScript source of truth.
- `generate_schema.py` turns the model into the schema consumed by editors and validation.

Agents should prefer reading/writing this config over hardcoding values.

## Data Flow for a Typical "Start Working" Session

1. Human clones repo.
2. Opens in VS Code → Dev Container rebuild.
3. `initializeCommand` → `init-env.sh` (generates `.env` with secrets on the **host**).
4. Container starts.
5. `postStartCommand` → `setup-payload.sh` (creates the Payload project if missing, using config + live secrets).
6. Agent/Human runs `xde dev`.
7. `xde` checks if services are up → calls `up` if needed.
8. `xde` performs DB readiness check.
9. `xde` changes into the generated project directory and runs `pnpm dev`.

The goal is for step 6 (`xde dev`) to become the only thing a human or agent needs to remember.

## Migration Philosophy

We are deliberately **not** porting the entire Makefile 1:1.

Instead we are:
- Identifying the *valuable outcomes* the Makefile delivered.
- Re-implementing them in a cleaner, more testable, more agent-friendly way inside `xde`.
- Adding strong guardrails and better UX along the way.

Destructive operations in particular (`reset-project`) are being given much more thought and safety than they had in the Makefile era.

## Key Invariants Agents Must Respect

- Never assume you're inside the container unless `EnvironmentContext` says so.
- Prefer `xde` commands over direct `docker compose` or shell scripts.
- Treat `create-payload-config.json` as the source of truth for project generation parameters.
- Be extremely careful with anything that touches the generated Payload project folder or the Postgres volume.

**Agent Tip**: At the start of any non-trivial task, explicitly state which layer you believe you are operating in and which abstraction (`EnvironmentContext`, `DockerComposeController`, config, etc.) you will use. This reduces errors.

---

This architecture exists to make both human developers and AI agents dramatically more productive when building serious Payload CMS applications.