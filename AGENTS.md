# AI Agent Instructions — XGIC Payload CMS Dev Containers

Public repository. Multi-repo standards: https://github.com/xgic/ai  
Architecture: [ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md)

## Product

This repository is a **Payload CMS Dev Container template / consumer**.  
It does **not** own the CLI implementation.

| Concern | Package | Repository |
|---------|---------|------------|
| CLI framework | `xgic.cli` | https://github.com/xgic/cli |
| Compose / lifecycle | `xgic.cli.dev` | https://github.com/xgic/dev-cli |
| Payload CMS commands | `xgic.cli.payload` | https://github.com/xgic/payload-cms-cli |

**Brand:** **XGIC CLI** only in living docs. No supported `xde` entrypoint (hard cutover complete for this template).

**Install source:** consumers install **from PyPI** with version pins (`uv pip install xgic-cli…`), not from live Git `main`. See [python-package-release.md](https://github.com/xgic/ai/blob/main/docs/python-package-release.md).

## Session startup

Inside the Dev Container (`xgic` is on PATH):

1. `xgic --help`  
2. `xgic check`  
3. `xgic payload env`  
4. Daily work: `xgic payload dev`  
5. Destructive reset: `xgic payload reset --dry-run` then `--yes`  

## Command map (for agents)

| Action | Command |
|--------|---------|
| Help / version | `xgic --help` / `xgic --version` |
| Compose up / down | `xgic up` / `xgic down` (set profile if needed: `--profile postgres`) |
| Health | `xgic check` |
| Generic env status | `xgic env` |
| Payload env / regenerate | `xgic payload env` / `xgic payload env --regenerate --yes` |
| Smart app start | `xgic payload dev` |
| Ensure project | `xgic payload setup` |
| Schema | `xgic payload schema` |
| Targeted reset | `xgic payload reset --dry-run` / `--yes` |

Defaults for this template (also set in the image):

- `XGIC_COMPOSE_FILE=.devcontainer/docker-compose.yml`  
- `XGIC_COMPOSE_PROJECT=xgic-payload-cms-dev-containers`  
- `XGIC_PRIMARY_SERVICE=xgic-payload-cms-dev-containers`  

## Rules

- Public-safe content only (no private hosts, private tracker IDs, internal paths).  
- Human UI review before merge to `main`.  
- Dedicated issue-number branches; Conventional Commits; **labels required**.  
- Python 3.14+; Apache-2.0; root `CODEOWNERS` (`@xgic`).  
- Prefer full `https://github.com/xgic/...` URLs.  
- Do **not** reintroduce an in-tree CLI package or `xde` console script.  
- CLI changes belong in the modular repos above, not here.

## Local memory

Temporary status reports only under `.xgic/` (gitignored). Never commit `.xgic/`.
