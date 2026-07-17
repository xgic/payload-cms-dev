# Configuration Source & Schema

This directory contains the canonical definition of the devcontainer configuration.

- `types.ts` — The single source of truth (TypeScript interfaces + Zod schema).
- `generate_schema.py` — Generates `create-payload-config.schema.json` from the model.
- `create-payload-config.example.ts` — Example of using the typed configuration.

## Usage

- The main configuration file lives at the project root: `.devcontainer/create-payload-config.json`.
- It references the generated schema for rich VS Code IntelliSense and validation.
- After modifying `types.ts`, run `xgic payload schema` (or execute `.devcontainer/config/generate_schema.py` directly) to update the schema.

This approach keeps configuration simple (JSON for end users) while maintaining strong typing and excellent editor support.