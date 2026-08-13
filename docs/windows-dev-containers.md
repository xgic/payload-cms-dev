# Windows + Docker Desktop: Dev Containers notes

## Symptom

VS Code **Reopen in Container** fails with:

- `mkdir ... /root/.vscode-remote-containers/...: No space left on device`
- and/or `bash .devcontainer/scripts/init-env.sh` → `execvpe(/bin/bash) failed`

## Why `docker system prune` is not enough

Docker Desktop uses **two** storage layers:

| Layer | What it holds | Typical free space |
|-------|---------------|--------------------|
| Docker **data** disk | Images, containers, volumes | Large (GB–TB) — `docker system prune` reclaims **here** |
| WSL distro **`docker-desktop` root** (`/`, often ~128 MB) | Utility root + `/root` | Tiny — Dev Containers may install VS Code Server under `/root/.vscode-remote-containers` |

If the tiny root is **100% full**, VS Code Server install fails even when Docker data disk and Windows `C:` have hundreds of GB free.

Check:

```bash
wsl -d docker-desktop -e df -h /
wsl -d docker-desktop -e sh -c "du -sh /root/* /root/.[!.]* 2>/dev/null"
```

Safe cleanup of a **failed/incomplete** server install:

```bash
wsl -d docker-desktop -e sh -c "rm -rf /root/.vscode-remote-containers"
wsl -d docker-desktop -e df -h /
```

If `/` remains ~128 MB total and still cannot install the server, use Docker Desktop repair/update, or develop from a full Linux WSL distro with Docker integration (recommended long-term).

## Host Bash lifecycle hooks (removed)

Producer `devcontainer.json` no longer uses host `initializeCommand` / auto `postStartCommand` setup. Those required host `bash` and failed on many Windows setups.

**Inside the container**, run:

```bash
xgic payload env --regenerate --yes   # if .devcontainer/.env is missing
xgic payload setup
xgic payload dev
```

Template consumers using `ghcr.io/xgic/payload-cms-dev` follow the same CLI path.
