#!/usr/bin/env bash
# Host / mount helpers for gated Git DX inside the Dev Container.
# Prefer filesystem signals (e.g. 9p) over blunt "always Windows".
# shellcheck shell=bash

# Workspace path used for Git / mount checks (override for tests).
xgic_workspace_path() {
  printf '%s\n' "${XGIC_WORKSPACE:-${WORKSPACE:-/workspace}}"
}

# Optional explicit host hint: windows | linux | macos | darwin | unset.
# Used when FS detection is insufficient (especially SSH agent paths).
xgic_docker_host_os_hint() {
  printf '%s\n' "${XGIC_DOCKER_HOST_OS:-}" | tr '[:upper:]' '[:lower:]'
}

# Filesystem type for the workspace mount (best effort).
xgic_workspace_fstype() {
  local ws mounts="${XGIC_PROC_MOUNTS:-/proc/mounts}"
  ws="$(xgic_workspace_path)"

  if command -v findmnt >/dev/null 2>&1; then
    findmnt -n -o FSTYPE --target "$ws" 2>/dev/null && return 0
  fi

  if [ ! -r "$mounts" ]; then
    return 1
  fi

  # Longest mountpoint match from /proc/mounts (field 2 = target, 3 = type).
  # Require path-boundary prefix so /work does not match /workspace.
  awk -v ws="$ws" '
    BEGIN { best = -1; fstype = "" }
    {
      mp = $2
      gsub(/\\040/, " ", mp)
      if (ws == mp || index(ws, mp "/") == 1) {
        if (length(mp) > best) {
          best = length(mp)
          fstype = $3
        }
      }
    }
    END { if (best >= 0) print fstype }
  ' "$mounts"
}

# Bind-mount types that commonly report mismatched ownership to Git.
xgic_is_friction_fstype() {
  case "${1:-}" in
    9p | cifs | smbfs | drvfs | fuse.osxfs | fuse.virtiofs)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# True when workspace dir owner uid differs from the current euid.
xgic_workspace_owner_mismatch() {
  local ws owner
  ws="$(xgic_workspace_path)"
  [ -d "$ws" ] || return 1
  owner="$(stat -c '%u' "$ws" 2>/dev/null || true)"
  [ -n "$owner" ] || return 1
  [ "$owner" != "$(id -u)" ]
}

# Whether Git safe.directory should be applied for this workspace.
xgic_needs_git_safe_directory() {
  local hint fstype
  hint="$(xgic_docker_host_os_hint)"
  case "$hint" in
    windows)
      return 0
      ;;
  esac

  fstype="$(xgic_workspace_fstype || true)"
  if xgic_is_friction_fstype "$fstype"; then
    return 0
  fi

  # Secondary signal: root-owned bind mount while running as non-root.
  if [ "$(id -u)" -ne 0 ] && xgic_workspace_owner_mismatch; then
    return 0
  fi

  return 1
}

# Docker Desktop host-services SSH agent socket (Mac / some Windows DD).
xgic_dd_ssh_auth_sock() {
  printf '%s\n' \
    "${XGIC_DD_SSH_AUTH_SOCK:-/run/host-services/ssh-auth.sock}"
}

xgic_dd_ssh_auth_sock_present() {
  local sock
  sock="$(xgic_dd_ssh_auth_sock)"
  [ -S "$sock" ]
}

# Hint that Docker Desktop–style SSH agent plumbing is relevant.
xgic_needs_dd_ssh_agent_hint() {
  local hint
  hint="$(xgic_docker_host_os_hint)"
  case "$hint" in
    windows | macos | darwin)
      return 0
      ;;
    linux)
      return 1
      ;;
  esac
  xgic_dd_ssh_auth_sock_present
}
