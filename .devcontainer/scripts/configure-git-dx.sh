#!/usr/bin/env bash
# Idempotent, host-conditional Git DX for Dev Containers.
# - Git safe.directory only when FS / hint says it is needed
# - Ensure ~/.ssh is writable; seed public GitHub known_hosts
# - Prefer HTTPS + host credential helper (VS Code best practice)
# - Optional Docker Desktop SSH agent sock export when present
# Does NOT copy host private keys or set safe.directory '*'.
#
# Intended to run once per container start from Docker Compose
# (primary service command), not from devcontainer.json lifecycle hooks.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGGING_LIB="${SCRIPT_DIR}/lib/logging.sh"
HOST_FS_LIB="${SCRIPT_DIR}/lib/host-fs.sh"

if [ -f "$LOGGING_LIB" ]; then
  # shellcheck source=lib/logging.sh
  source "$LOGGING_LIB"
else
  log_info() { echo "[$1] $2"; }
  log_success() { echo "[$1] $2"; }
  log_warn() { echo "[$1] $2" >&2; }
  log_error() { echo "[$1] $2" >&2; }
  log_debug() { :; }
fi

# shellcheck source=lib/host-fs.sh
source "$HOST_FS_LIB"

PREFIX="git-dx"
DRY_RUN=0
STATUS_ONLY=0
# Quiet by default when invoked from Compose. Verbose for --status or
# XGIC_GIT_DX_VERBOSE=1 / --verbose.
QUIET=1
if [ "${XGIC_GIT_DX_VERBOSE:-0}" = "1" ]; then
  QUIET=0
fi

# Prefer HTTPS for github.com git@ remotes unless explicitly disabled.
# Uses host credential helper shared by VS Code Dev Containers.
PREFER_HTTPS="${XGIC_GIT_PREFER_HTTPS:-1}"

usage() {
  cat <<'EOF'
Usage: configure-git-dx.sh [--status] [--dry-run] [--verbose] [--quiet] [--help]

Host-conditional Git DX (safe.directory, known_hosts, HTTPS prefer, SSH hints).

  --status    Print detection results; make no changes (implies verbose)
  --dry-run   Show actions without applying them
  --verbose   Log detection status even when no changes are needed
  --quiet     Only log when applying a change or warning (default)
  --help      Show this help

Env:
  XGIC_WORKSPACE          Workspace path (default: /workspace)
  XGIC_DOCKER_HOST_OS     Optional hint: windows|linux|macos
  XGIC_DD_SSH_AUTH_SOCK   Docker Desktop SSH sock path override
  XGIC_PROC_MOUNTS        Override /proc/mounts (tests)
  XGIC_GIT_DX_VERBOSE=1   Same as --verbose
  XGIC_GIT_PREFER_HTTPS=0 Disable github.com SSH→HTTPS insteadOf rewrite
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --status)
      STATUS_ONLY=1
      QUIET=0
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --verbose)
      QUIET=0
      shift
      ;;
    --quiet)
      QUIET=1
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      log_error "$PREFIX" "Unknown option: $1"
      usage >&2
      exit 2
      ;;
  esac
done

ws="$(xgic_workspace_path)"
hint="$(xgic_docker_host_os_hint)"
fstype="$(xgic_workspace_fstype || true)"
needs_safe=0
needs_dd_ssh=0
if xgic_needs_git_safe_directory; then
  needs_safe=1
fi
if xgic_needs_dd_ssh_agent_hint; then
  needs_dd_ssh=1
fi

vlog_info() {
  if [ "$QUIET" -eq 0 ]; then
    log_info "$PREFIX" "$1"
  fi
}

ssh_dir() {
  printf '%s\n' "${HOME}/.ssh"
}

ssh_agent_usable() {
  [ -n "${SSH_AUTH_SOCK:-}" ] && [ -S "${SSH_AUTH_SOCK}" ]
}

print_status() {
  vlog_info "workspace=${ws}"
  vlog_info "fstype=${fstype:-unknown}"
  vlog_info "XGIC_DOCKER_HOST_OS=${hint:-unset}"
  vlog_info "needs_safe_directory=${needs_safe}"
  vlog_info "needs_dd_ssh_hint=${needs_dd_ssh}"
  vlog_info "XGIC_GIT_PREFER_HTTPS=${PREFER_HTTPS}"
  if xgic_dd_ssh_auth_sock_present; then
    vlog_info "dd_ssh_sock=present ($(xgic_dd_ssh_auth_sock))"
  else
    vlog_info "dd_ssh_sock=absent"
  fi
  if ssh_agent_usable; then
    vlog_info "SSH_AUTH_SOCK=${SSH_AUTH_SOCK} (usable)"
  elif [ -n "${SSH_AUTH_SOCK:-}" ]; then
    vlog_info "SSH_AUTH_SOCK=${SSH_AUTH_SOCK} (not a socket)"
  else
    vlog_info "SSH_AUTH_SOCK=unset"
  fi
  local sd
  sd="$(ssh_dir)"
  if [ -d "$sd" ]; then
    vlog_info "ssh_dir=${sd} owner=$(stat -c '%U:%G' "$sd" 2>/dev/null || echo unknown)"
  else
    vlog_info "ssh_dir=${sd} (missing)"
  fi
}

safe_directory_configured() {
  local entry
  entry="$(git config --global --get-all safe.directory 2>/dev/null || true)"
  printf '%s\n' "$entry" | grep -qx "$ws"
}

configure_safe_directory() {
  if safe_directory_configured; then
    log_debug "$PREFIX" "safe.directory already includes ${ws}"
    return 0
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    log_info "$PREFIX" \
      "dry-run: git config --global --add safe.directory ${ws}"
    return 0
  fi
  git config --global --add safe.directory "$ws"
  log_success "$PREFIX" "Added safe.directory ${ws}"
}

# Ensure ~/.ssh exists and is writable by the current user (named volumes
# often initialize as root:root, which blocks known_hosts updates).
ensure_ssh_dir() {
  local sd
  sd="$(ssh_dir)"
  if [ "$DRY_RUN" -eq 1 ]; then
    log_info "$PREFIX" "dry-run: ensure ${sd} mode 700 and writable"
    return 0
  fi
  if [ ! -d "$sd" ]; then
    if ! mkdir -p "$sd" 2>/dev/null; then
      log_warn "$PREFIX" \
        "Cannot create ${sd}. Fix ownership of the ssh-home volume (node:node)."
      return 1
    fi
  fi
  chmod 700 "$sd" 2>/dev/null || true
  if [ ! -w "$sd" ]; then
    log_warn "$PREFIX" \
      "${sd} is not writable by $(id -un) (often a root-owned named volume)."
    log_warn "$PREFIX" \
      "Compose startup should chown it to node before this script runs."
    return 1
  fi
  return 0
}

# Public GitHub SSH host keys only (not secrets).
# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints
seed_github_known_hosts() {
  local sd kh marker
  sd="$(ssh_dir)"
  kh="${sd}/known_hosts"
  marker="github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl"

  if [ "$DRY_RUN" -eq 1 ]; then
    log_info "$PREFIX" "dry-run: seed GitHub keys into ${kh}"
    return 0
  fi
  if ! ensure_ssh_dir; then
    return 1
  fi
  touch "$kh"
  chmod 600 "$kh" 2>/dev/null || true
  if grep -Fq "$marker" "$kh" 2>/dev/null; then
    log_debug "$PREFIX" "GitHub known_hosts already seeded"
    return 0
  fi
  {
    printf '%s\n' \
      "github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl" \
      "github.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=" \
      "github.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCj7ndNxQowgcQnjshcLrqPEiiphnt+VTTvDP6mHBL9j1aNUkY4Ue1gvwnGLVlOhGeYrnZaMg93xq+21Bx9EONXG/d6INRD3xey1OVJrT2JBwxfA0bOJRTTWe+l1ahNDU9fKk5xvhS+gF7OEIc0DIbKTwSjNbBaEKWkf3m/ueIWIKpG+7V7d8="
  } >>"$kh"
  log_success "$PREFIX" "Seeded GitHub SSH host keys into known_hosts"
}

https_insteadof_configured() {
  git config --global --get-regexp \
    '^url\.https://github\.com/\.insteadof$' >/dev/null 2>&1
}

# Map git@github.com:… to https://github.com/… so VS Code can reuse the
# host credential helper. Does not copy tokens or private keys.
configure_github_https_insteadof() {
  case "${PREFER_HTTPS}" in
    0 | false | FALSE | no | NO)
      vlog_info "HTTPS insteadOf disabled (XGIC_GIT_PREFER_HTTPS=${PREFER_HTTPS})"
      return 0
      ;;
  esac

  if https_insteadof_configured; then
    log_debug "$PREFIX" "github.com HTTPS insteadOf already set"
    return 0
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    log_info "$PREFIX" \
      "dry-run: git config --global url.https://github.com/.insteadOf git@github.com:"
    return 0
  fi
  # --add: both insteadOf values must coexist (a second write would replace).
  git config --global --add url.https://github.com/.insteadOf git@github.com:
  git config --global --add url.https://github.com/.insteadOf ssh://git@github.com/
  log_success "$PREFIX" \
    "Prefer HTTPS for github.com (host credential helper; no private keys copied)"
}

bashrc_snippet_path() {
  printf '%s\n' "${HOME}/.config/xgic/git-dx-ssh.sh"
}

# Persist SSH_AUTH_SOCK for interactive shells when DD sock is mounted.
install_ssh_bashrc_snippet() {
  local sock snippet marker rc
  sock="$(xgic_dd_ssh_auth_sock)"
  snippet="$(bashrc_snippet_path)"
  marker="# XGIC git-dx SSH agent (managed)"
  rc="${HOME}/.bashrc"

  if [ "$DRY_RUN" -eq 1 ]; then
    log_info "$PREFIX" \
      "dry-run: write ${snippet} and source from ~/.bashrc"
    return 0
  fi

  mkdir -p "$(dirname "$snippet")"
  cat >"$snippet" <<EOF
# Generated by configure-git-dx.sh — do not store secrets here.
${marker}
_xgic_dd_sock='${sock}'
if [ -S "\${_xgic_dd_sock}" ]; then
  export SSH_AUTH_SOCK="\${_xgic_dd_sock}"
fi
unset _xgic_dd_sock
EOF

  touch "$rc"
  if ! grep -Fq "$snippet" "$rc" 2>/dev/null; then
    {
      printf '\n%s\n' "$marker"
      printf '[ -f "%s" ] && . "%s"\n' "$snippet" "$snippet"
    } >>"$rc"
  fi

  if [ -S "$sock" ]; then
    export SSH_AUTH_SOCK="$sock"
  fi
  log_success "$PREFIX" "SSH agent snippet ready (${sock})"
}

print_ssh_guidance() {
  if ssh_agent_usable; then
    vlog_info "SSH agent socket already available"
    return 0
  fi
  if xgic_dd_ssh_auth_sock_present; then
    install_ssh_bashrc_snippet
    return 0
  fi
  case "${PREFER_HTTPS}" in
    0 | false | FALSE | no | NO)
      if [ "$needs_dd_ssh" -eq 1 ]; then
        log_warn "$PREFIX" \
          "No SSH agent in the container. Opt in Docker Desktop sock fragment:"
        log_warn "$PREFIX" \
          "  .devcontainer/docker-compose.git-dx.yml"
        log_warn "$PREFIX" \
          "Or set XGIC_GIT_PREFER_HTTPS=1 (default) to use HTTPS + host credentials."
      else
        log_warn "$PREFIX" \
          "No SSH agent (SSH_AUTH_SOCK unset). Start ssh-agent on the host,"
        log_warn "$PREFIX" \
          "ssh-add your key, and reopen so VS Code can forward the agent —"
        log_warn "$PREFIX" \
          "or use HTTPS (XGIC_GIT_PREFER_HTTPS=1, default)."
      fi
      ;;
    *)
      vlog_info \
        "SSH agent not required when github.com HTTPS insteadOf is enabled"
      ;;
  esac
}

print_status

if [ "$STATUS_ONLY" -eq 1 ]; then
  exit 0
fi

if [ "$needs_safe" -eq 1 ]; then
  configure_safe_directory
else
  vlog_info "Skipping safe.directory (not needed on this mount)"
fi

# known_hosts + HTTPS prefer run on every supported host (cheap, idempotent).
seed_github_known_hosts || true
configure_github_https_insteadof
print_ssh_guidance

exit 0
