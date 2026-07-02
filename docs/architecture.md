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

4. **Legacy Automation** (retired in 0.1.0)
   - Earlier shell/Python scripts in `.devcontainer/scripts/`.
   - Migration to `xde` as the single, testable interface is complete. Historical context is preserved in the primary plan and platform issues/tasks (and git history).

## Core Abstractions (Most Important for Agents)

### EnvironmentContext (`src/xde/core/environment.py`)

Tells you where you are running:
- `HOST`
- `DEV_CONTAINER`
- `GENERIC_CONTAINER`

This replaces fragile environment-guard patterns from earlier automation.

**Always** start by understanding the environment context when reasoning about a task.

### DockerComposeController (`src/xde/core/docker.py`)

The single place that talks to Docker and Docker Compose.

**Current strategy (as of 2026):**
We are deliberately using a simple subprocess-based implementation
(calling the `docker` and `docker compose` CLI). The operations we
perform today are relatively straightforward, so we do not need
additional complexity at this stage.

**Future consideration:**
We will periodically re-evaluate this module and may rewrite it in the
future to use a more advanced interface (e.g. `python-on-whales`, the
official Docker Python SDK, or a small Go helper binary using Docker's
official Go Compose SDK) once our requirements grow more complex.

Current responsibilities:
- Start/stop/build services
- Query service status
- Execute commands inside containers
- Basic health checks and volume management

See the "CURRENT STRATEGY & FUTURE CONSIDERATION" section in
`src/xde/core/docker.py` and the corresponding item in the primary plan and platform issues/tasks.

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

## Migration Philosophy (Historical)

The implementation deliberately did not port the entire earlier automation approach 1:1.

Instead the approach was:
- Identifying the *valuable outcomes* the earlier automation delivered.
- Re-implementing them in a cleaner, more testable, more agent-friendly way inside `xde`.
- Adding strong guardrails and better UX along the way.

Destructive operations in particular (now `xde reset`) are given strong guardrails, targeted postgres handling, and clean UX (no self-recreate of the caller's container when running reset from inside the dev container). This was a major improvement over the earlier automation era.

## Key Invariants Agents Must Respect

- Never assume you're inside the container unless `EnvironmentContext` says so.
- Prefer `xde` commands over direct `docker compose` or shell scripts.
- Treat `create-payload-config.json` as the source of truth for project generation parameters.
- Be extremely careful with anything that touches the generated Payload project folder or the PostgreSQL data volume.

**Agent Tip**: At the start of any non-trivial task, explicitly state which layer you believe you are operating in and which abstraction (`EnvironmentContext`, `DockerComposeController`, config, etc.) you will use. This reduces errors.

---

This architecture exists to make both human developers and AI agents dramatically more productive when building serious Payload CMS applications.