# AI Agent Instructions — XGIC Payload CMS Dev Containers

Public repository. Multi-repo standards: https://github.com/xgic/ai  
Architecture: [ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md)

## Product

This repository is the **Payload CMS Dev Container image producer** (`ghcr.io/xgic/payload-cms-dev`).  
It does **not** own the CLI implementation. End-user apps start from https://github.com/xgic/payload-cms.

| Concern | Package | Repository |
|---------|---------|------------|
| CLI framework | `xgic.cli` | https://github.com/xgic/cli |
| Docker Compose / lifecycle | `xgic.cli.dev` | https://github.com/xgic/dev-cli |
| Payload CMS commands | `xgic.cli.payload` | https://github.com/xgic/payload-cms-cli |

**Brand:** **XGIC CLI** only in living docs. No supported `xde` entrypoint (hard cutover complete for this template).

**Install source:** consumers install **from PyPI** with version pins (`uv pip install xgic-cli…`), not from live Git `main`. See [python-package-release.md](https://github.com/xgic/ai/blob/main/docs/python-package-release.md).

## Docker Compose–first consumer contract

Supported consumer Dev Container reopen is **Docker Compose** attached to the
pinned GHCR image service—**not** a standalone `image:` in `devcontainer.json`.

| Piece | Contract |
|-------|----------|
| Attach | `dockerComposeFile` + `service` (exemplar: this repo’s `.devcontainer/`) |
| Image pin (apps) | `image: ghcr.io/xgic/payload-cms-dev:<semver>` on the Docker Compose primary service |
| Stable project | Docker Compose `name:` + `XGIC_COMPOSE_*` + `composeProjectName` kept aligned |
| Database | Same Docker Compose project as the IDE attach |

**Anti-pattern:** image-only reopen → Docker’s default `adjective_noun` container
names, DB outside the IDE project, CLI / `composeProjectName` mismatch. Rebuild
once after switching to Docker Compose.

Thin template implementation:
[payload-cms#10](https://github.com/xgic/payload-cms/issues/10) /
[PR #11](https://github.com/xgic/payload-cms/pull/11). Full write-up:
[docs/architecture.md](docs/architecture.md#consumer-contract-docker-compose-first).
Workspace filesystem: [docs/dev-performance.md](docs/dev-performance.md)
(native Linux / WSL2; this producer does not overlay `app/node_modules`).

Related: [payload-cms-cli#26](https://github.com/xgic/payload-cms-cli/issues/26)
(env sync), [#49](https://github.com/xgic/payload-cms-dev/issues/49) /
[#61](https://github.com/xgic/payload-cms-dev/issues/61)
(host-conditional Git DX in the GHCR image entrypoint).

## Session startup

Inside the Dev Container (`xgic` is on PATH, including login shells via
`/etc/profile.d/xgic-cli.sh`):

1. `xgic --help`  
2. `xgic check`  
3. `xgic payload setup` — env + DB (`dbAdapter`, default PostgreSQL) + scaffold under **`app/`**, **or** `pnpx create-payload-app@latest app`  
4. Daily work: `xgic payload dev` (requires an app under `app/`). First HTTP
   request is a cold Turbopack compile of the website template (tens of
   seconds); later requests are much faster. Next.js 16.3 may log
   `The destination stream closed early` when opening `/admin` (client-aborted
   RSC stream; `GET /admin` still 200). The document is an RSC shell — a blank
   browser tab with HTTP 200 is that abort, not a missing Postgres database.
   Postgres `FATAL: database "payload" does not exist` is libpq defaulting to
   the user name; the app database is `payload_db` (`PGDATABASE` / `DATABASE_URL`).  
5. Destructive reset: `xgic payload reset --dry-run` then `--yes`  

Do **not** reintroduce `initializeCommand` / `postAttachCommand` /
`postStartCommand` / `postCreateCommand` hooks for Git DX.

### Host-conditional Git DX (portable contract for all XGIC Dev Containers)

Image-owned (no `devcontainer.json` lifecycle hooks; not vendored into app
repos). Scripts are installed at `/usr/local/lib/xgic/git-dx/` so the
`/workspace` bind-mount cannot hide them. `/usr/local/bin/xgic-devcontainer-entrypoint`
runs once per container start:

1. If root: chown `ssh-home` → `node`, align the image `docker` group to the
   engine socket GID (hosts vary; do not hard-code a GID).
2. `configure-git-dx.sh --quiet` as `node`. Failure is **non-fatal**
   (keep-alive always continues).
3. `exec` Compose `command` / image `CMD`.

Consumers: pin the GHCR image, set Compose `user: "0:0"`, mount `ssh-home`,
optional Desktop SSH overlay. Do **not** copy these scripts into the app
tree.

**Git auth (VS Code best practice):**

1. **HTTPS + host credential helper** (default).
2. **SSH agent** optional/advanced (VS Code forwarding or opt-in Compose fragment).
3. **Never** copy host private keys into the image/volume by default.

Default `dbAdapter` is `postgres`. For MongoDB (and later adapters), set
`dbAdapter` in `.devcontainer/create-payload-config.json` **before** `xgic payload setup`.

Overrides: `XGIC_GIT_PREFER_HTTPS=0|1`, `XGIC_DOCKER_HOST_OS=windows|linux|macos`.  
Status: `bash /usr/local/lib/xgic/git-dx/configure-git-dx.sh --status`

## Command map (for agents)

| Action | Command |
|--------|---------|
| Help / version | `xgic --help` / `xgic --version` |
| Docker Compose up / down | `xgic up` / `xgic down` (set profile if needed: `--profile postgres`) |
| Health | `xgic check` |
| Generic env status | `xgic env` |
| Payload env / regenerate | `xgic payload env` / `xgic payload env --regenerate --yes` |
| Smart app start | `xgic payload dev` |
| Ensure project | `xgic payload setup` |
| Schema | `xgic payload schema` |
| Targeted reset | `xgic payload reset --dry-run` / `--yes` |

Defaults for this template (also set in the image):

- `XGIC_COMPOSE_FILE=.devcontainer/docker-compose.yml`  
- `XGIC_COMPOSE_PROJECT=xgic-payload-cms-dev`  
- `XGIC_PRIMARY_SERVICE=xgic-payload-cms-dev`  

## Rules


**Public GitHub writes:** Before `gh issue create|edit`, `gh pr create|edit`, or any public comment on this repository, complete the **mandatory public-safe draft gate** in https://github.com/xgic/ai/blob/main/docs/BASE-STANDARDS-FOR-ORCHESTRATED-REPOS.md (fictional placeholders only; never name private hosts, private projects, or private tracker IDs). Optional helper from the hub clone: `python scripts/public-safe-scan.py path/to/draft.md`.
- Public-safe content only (no private hosts, private tracker IDs, internal paths).  
- Human UI review before merge to `main`.  
- Dedicated issue-number branches; Conventional Commits; **labels required**.  
- Python 3.14+; Apache-2.0; root `CODEOWNERS` (`@xgic`).  
- Prefer full `https://github.com/xgic/...` URLs.  
- Do **not** reintroduce an in-tree CLI package or `xde` console script.  
- Do **not** regress consumers to standalone `image:` reopen; keep Docker Compose–first.  
- CLI changes belong in the modular repos above, not here.

## Local memory

Temporary status reports only under `.xgic/` (gitignored). Never commit `.xgic/`.

