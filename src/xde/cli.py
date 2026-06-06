"""CLI entrypoint for xde.

This is the main command-line interface for the XGIC Dev Environment.

Design goals (especially important for agentic use):
- Small, predictable command surface (no aliases, one clear way to do things).
- Excellent default behavior with clear escape hatches (`--yes`, `--dry-run`).
- High-quality output using Rich (panels + graceful
  color fallback).
- Strong environment awareness via `EnvironmentContext`.

The CLI is deliberately built using only stdlib + Rich + Pydantic to keep
the dependency footprint minimal and contributor-friendly.

See `AGENTS.md` and `docs/grok-playbooks.md` for how Grok Build is expected
to interact with this interface.
"""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from xde import __version__
from xde.commands.dev import run_dev
from xde.commands.diagnostics import run_check
from xde.commands.env import run_env
from xde.commands.lifecycle import (
    run_build,
    run_clean,
    run_down,
    run_logs,
    run_shell,
    run_up,
)
from xde.commands.reset import run_reset
from xde.core.docker import DockerComposeController
from xde.core.environment import EnvironmentContext
from xde.utils.output import print_error

console = Console()


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="xde",
        description=(
            "XGIC Dev Environment CLI - reliable dev container orchestration"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  xde dev          Smart start of Payload dev server (recommended daily command)
  xde up           Start all services
  xde reset        Fast targeted reset (project folder + Postgres volume)
  xde check        Health diagnostics
        """,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    # dev - the smart primary command
    dev_parser = subparsers.add_parser(
        "dev",
        help="Start the Payload development server (recommended daily command)",
    )
    dev_parser.set_defaults(func=run_dev)

    # up
    up_parser = subparsers.add_parser(
        "up", help="Start all development services"
    )
    up_parser.set_defaults(func=run_up)

    # down
    down_parser = subparsers.add_parser(
        "down", help="Stop containers (volumes preserved)"
    )
    down_parser.set_defaults(func=run_down)

    # reset
    reset_parser = subparsers.add_parser(
        "reset",
        help="Fast targeted reset (project folder + Postgres volume)",
    )
    reset_parser.add_argument(
        "--yes", action="store_true", help="Skip confirmation prompt"
    )
    reset_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    reset_parser.add_argument(
        "--rotate-credentials",
        action="store_true",
        help="Also generate fresh database password and PAYLOAD_SECRET",
    )
    reset_parser.add_argument(
        "--compact",
        action="store_true",
        help="Compact output (for make shims / scripting)",
    )
    reset_parser.set_defaults(func=run_reset)

    # check
    check_parser = subparsers.add_parser(
        "check",
        help="Diagnostic: verify PostgreSQL and services are reachable",
    )
    check_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (useful for scripts/agents)",
    )
    check_parser.set_defaults(func=run_check)

    # build (with useful flags instead of many Makefile variants)
    build_parser = subparsers.add_parser(
        "build",
        help="Build or rebuild services (use --no-cache for clean build)",
    )
    build_parser.add_argument(
        "--no-cache", action="store_true", help="Build without cache"
    )
    build_parser.set_defaults(func=run_build)

    # logs
    logs_parser = subparsers.add_parser(
        "logs", help="Follow logs for all services"
    )
    logs_parser.set_defaults(func=run_logs)

    # shell
    shell_parser = subparsers.add_parser(
        "shell", help="Open interactive shell in the primary service"
    )
    shell_parser.set_defaults(func=run_shell)

    # env (lightweight environment inspection / management)
    env_parser = subparsers.add_parser(
        "env", help="Inspect and manage the generated environment"
    )
    env_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (useful for scripts/agents)",
    )
    env_parser.set_defaults(func=run_env)

    # clean (more destructive, with strong safeguards)
    clean_parser = subparsers.add_parser(
        "clean",
        help="[DANGER] Full environment cleanup (volumes + .env)",
    )
    clean_parser.add_argument(
        "--yes", action="store_true", help="Skip confirmation"
    )
    clean_parser.set_defaults(func=run_clean)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        # Initialize context (OOP environment detection)
        env = EnvironmentContext.detect()
        docker = DockerComposeController(env)

        # Dispatch
        result = args.func(args, env=env, docker=docker)
        return 0 if result is None else result

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        return 130
    except Exception as exc:
        print_error(f"Unexpected error: {exc}")
        if "--debug" in (argv or sys.argv):
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
