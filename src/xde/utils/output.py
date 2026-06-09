"""Rich-based output helpers.

Proper runtime detection for colors and emoji (no fragile parse-time
TTY/emoji hacks from the previous Makefile). This permanently solves the
emoji/TTY problems we had in the old Makefile implementation.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

console = Console()


# Simple runtime emoji policy (can be made more sophisticated later)
def _should_use_emoji() -> bool:
    """Decide at runtime whether to use emoji."""
    import os

    if os.environ.get("NO_COLOR") or os.environ.get("EMOJI") == "0":
        return False
    # Rich's own detection is excellent; we just ask it
    return console.is_terminal and not console.is_dumb_terminal


def print_error(message: str) -> None:
    """Print a clear error with optional emoji."""
    prefix = "❌ " if _should_use_emoji() else "[ERROR] "
    console.print(f"{prefix}{message}", style="bold red")


def print_success(message: str) -> None:
    """Print success message."""
    prefix = "✅ " if _should_use_emoji() else "[OK] "
    console.print(f"{prefix}{message}", style="bold green")


def print_info(message: str) -> None:
    """Print informational message."""
    prefix = "ℹ️  " if _should_use_emoji() else "[INFO] "
    console.print(f"{prefix}{message}")


def print_warning(message: str) -> None:
    """Print warning."""
    prefix = "⚠️  " if _should_use_emoji() else "[WARN] "
    console.print(f"{prefix}{message}", style="yellow")


def print_panel(title: str, content: str, style: str = "blue") -> None:
    """Print a nice panel (useful for status, errors, etc.)."""
    console.print(Panel(content, title=title, border_style=style))
