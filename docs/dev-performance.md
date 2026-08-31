# Dev performance (workspace filesystem)

Producer guidance. Application templates: [payload-cms `docs/dev-performance.md`](https://github.com/xgic/payload-cms/blob/main/docs/dev-performance.md).

## Supported layout

Keep the **workspace on a native Linux filesystem** the Docker engine can serve with low latency:

- Linux Docker host path, or
- **WSL2** filesystem on Windows (Docker Desktop WSL2 engine)

`pnpm install` and the first Payload `/admin` compile stay in one tree with `node_modules` and `.next`. **Do not** bind-mount an NTFS path (`C:\…`) into the producer Dev Container; that path is unsupported.

This producer does **not** mount named volumes over `app/node_modules` or `app/.next` (those overlays hide installs and break `pnpx create-payload-app` / `xgic payload setup`).

## What this does **not** change

- Supported reopen remains **Docker Compose** (`dockerComposeFile` + service). See [architecture.md](architecture.md#consumer-contract-docker-compose-first).
- Credentials: `.devcontainer/.env` vs app `.env` — [payload-cms-cli#26](https://github.com/xgic/payload-cms-cli/issues/26).

## Related

- Consumer contract: [#50](https://github.com/xgic/payload-cms-dev/issues/50)
- Template Compose-first reopen: [payload-cms#10](https://github.com/xgic/payload-cms/issues/10) / [PR #11](https://github.com/xgic/payload-cms/pull/11)
- Git DX: [#49](https://github.com/xgic/payload-cms-dev/issues/49), template [payload-cms#9](https://github.com/xgic/payload-cms/issues/9)
