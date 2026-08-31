#!/usr/bin/env python3
"""Align the image ``docker`` group to the engine socket GID.

Linux Docker sockets are often ``root:<engine-gid>`` mode ``660``. Images that
hard-code a docker GID (this producer uses 994 at build time) cannot talk to
the API when the host GID differs. Match the live socket instead of assuming
any particular number.

Run as root from the Compose primary command (same prelude as Git DX).
Failure is non-fatal so keep-alive still starts.
"""

from __future__ import annotations

import argparse
import grp
import os
import pwd
import stat
import subprocess
import sys
from dataclasses import dataclass

DEFAULT_SOCK = "/var/run/docker.sock"
DEFAULT_USER = os.environ.get("APP_USER", "node")
DEFAULT_GROUP = "docker"


@dataclass(frozen=True)
class AlignPlan:
    """Host-agnostic actions to grant *user* access to the engine socket."""

    groupmod_docker_to: int | None = None
    add_user_to_groups: tuple[str, ...] = ()
    reason: str = "noop"


def socket_gid(path: str) -> int | None:
    try:
        st = os.stat(path)
    except OSError:
        return None
    if not stat.S_ISSOCK(st.st_mode):
        return None
    return int(st.st_gid)


def groups_by_gid() -> dict[int, str]:
    found: dict[int, str] = {}
    for entry in grp.getgrall():
        found[int(entry.gr_gid)] = entry.gr_name
    return found


def group_gid(name: str) -> int | None:
    try:
        return int(grp.getgrnam(name).gr_gid)
    except KeyError:
        return None


def plan_align(
    sock_gid: int | None,
    *,
    docker_gid: int | None,
    gid_owners: dict[int, str],
    docker_group: str = DEFAULT_GROUP,
) -> AlignPlan:
    """Return actions without mutating the system.

    ``sock_gid`` 0 (root) is left unchanged: access is then mode-based (for
    example ``666``), not supplementary-group based.
    """
    if sock_gid is None or sock_gid == 0:
        return AlignPlan(reason="no-group-socket")
    if docker_gid == sock_gid:
        return AlignPlan(
            add_user_to_groups=(docker_group,),
            reason="already-matched",
        )
    owner = gid_owners.get(sock_gid)
    if owner and owner != docker_group:
        return AlignPlan(
            add_user_to_groups=(owner,),
            reason="join-existing-gid-group",
        )
    if docker_gid is None:
        return AlignPlan(reason="no-docker-group")
    return AlignPlan(
        groupmod_docker_to=sock_gid,
        add_user_to_groups=(docker_group,),
        reason="groupmod-docker",
    )


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def apply_plan(plan: AlignPlan, *, user: str, docker_group: str) -> int:
    try:
        pwd.getpwnam(user)
    except KeyError:
        print(f"[docker-sock] user {user!r} missing", file=sys.stderr)
        return 1
    if plan.groupmod_docker_to is not None:
        proc = _run(
            ["groupmod", "-g", str(plan.groupmod_docker_to), docker_group]
        )
        if proc.returncode != 0:
            print(
                f"[docker-sock] groupmod failed: {proc.stderr.strip()}",
                file=sys.stderr,
            )
            return proc.returncode
        print(
            f"[docker-sock] {docker_group} gid -> {plan.groupmod_docker_to}"
        )
    for group in plan.add_user_to_groups:
        proc = _run(["usermod", "-aG", group, user])
        if proc.returncode != 0:
            print(
                f"[docker-sock] usermod -aG {group} failed: "
                f"{proc.stderr.strip()}",
                file=sys.stderr,
            )
            return proc.returncode
        print(f"[docker-sock] {user} supplementary group {group}")
    if plan.reason in {"no-group-socket", "no-docker-group"}:
        print(f"[docker-sock] skip ({plan.reason})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sock", default=DEFAULT_SOCK)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--docker-group", default=DEFAULT_GROUP)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the plan and exit 0 without changing groups.",
    )
    args = parser.parse_args(argv)
    sock = socket_gid(args.sock)
    plan = plan_align(
        sock,
        docker_gid=group_gid(args.docker_group),
        gid_owners=groups_by_gid(),
        docker_group=args.docker_group,
    )
    if args.dry_run:
        print(
            f"[docker-sock] dry-run sock_gid={sock} reason={plan.reason} "
            f"groupmod={plan.groupmod_docker_to} "
            f"groups={plan.add_user_to_groups}"
        )
        return 0
    return apply_plan(
        plan, user=args.user, docker_group=args.docker_group
    )


if __name__ == "__main__":
    raise SystemExit(main())
