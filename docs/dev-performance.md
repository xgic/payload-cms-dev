# Dev performance (bind-mounted workspaces)

Producer guidance for humans and agents. The thin template documents the same
contract for application teams:
[payload-cms `docs/dev-performance.md`](https://github.com/xgic/payload-cms/blob/main/docs/dev-performance.md).

## Symptom

`pnpm install` and the first Payload `/admin` compile can be very slow when the
workspace is **bind-mounted** from the Docker host into the Dev Container and
that host filesystem has high latency for large Node module graphs.
`xgic payload dev` may report Ready while Turbopack is still walking the
module graph.

This stack supports **Windows and Linux Docker hosts equally**. Guidance below
applies on either host whenever bind-mount I/O dominates.

## Preferred long-term layout

Keep the **workspace on a native Linux filesystem** that the Docker engine
serves with low latency (for example a Linux VM disk, WSL2 filesystem, or a
Linux Docker host path—not a high-latency host share into the container).
Source, `node_modules`, and `.next` then share one coherent tree without a
volume overlay.

## Optional named-volume bridge (explicit, documented)

When the workspace must stay on a slower bind mount, Docker Compose may mount
**named volumes** over the hot module-graph paths so installs and Turbopack use
container-native storage while application source stays on the bind mount.

This is an **explicit documented bridge**, not a silent hack. The thin template
([payload-cms](https://github.com/xgic/payload-cms)) implements it for
**app-root** layout:

| Layout | Container paths | Typical volume names |
|--------|-----------------|----------------------|
| Template (app-root) | `/workspace/node_modules`, `/workspace/.next` | `xgic-payload-cms-dev-node-modules`, `xgic-payload-cms-dev-next` |
| Producer smoke (`app/`) | `/workspace/app/node_modules`, `/workspace/app/.next` if you add the same pattern | Keep names aligned with Docker Compose `name:` |

Ownership of those volumes should be corrected only when the mount is not
already owned by uid `1000` (`node`).

After you recreate those volumes (or the first time they are empty):

```bash
pnpm install
```

Run that from the Payload app root for the layout in use (`/` in the template;
`app/` in this producer).

## What this does **not** change

- Supported reopen remains **Docker Compose** (`dockerComposeFile` + service),
  never a standalone `image:` in `devcontainer.json`. See
  [architecture.md](architecture.md#consumer-contract-docker-compose-first).
- Credential files (`.devcontainer/.env` vs app `.env`) are not a performance
  workaround. Sync after regenerate is tracked in
  [payload-cms-cli#26](https://github.com/xgic/payload-cms-cli/issues/26).

## Related

- Consumer contract (this repo): [#50](https://github.com/xgic/payload-cms-dev/issues/50)
- Template Compose-first reopen: [payload-cms#10](https://github.com/xgic/payload-cms/issues/10) /
  [PR #11](https://github.com/xgic/payload-cms/pull/11)
- Host-conditional Git DX (safe.directory / SSH agent): [#49](https://github.com/xgic/payload-cms-dev/issues/49),
  template follow-up [payload-cms#9](https://github.com/xgic/payload-cms/issues/9)
