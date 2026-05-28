"""Run Ansible test playbooks with the Ansible Python API."""
import os
import subprocess
import sys

from ansible.cli.playbook import PlaybookCLI
from rich import inspect
from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    """Main function.

    1. Runs Ansible Lint.
    """
    ansible_file: str = sys.argv[1]

    subprocess.call("reset")

    # Header
    console.print(
        Panel(
            f"Starting {os.path.realpath(__file__)}",
            title="Linting Ansible File",
            subtitle=f"{ansible_file})",
            style=("bold black on cyan"),
        )
    )
    console.rule("[bold cyan]Running Ansible Lint.")
    args = ["ansible-lint", ansible_file]

    try:
        subprocess.run(args, capture_output=False, check=True)
    except subprocess.CalledProcessError as error:
        console.print(f"RETURN_CODE: {error.returncode}\n")
        # inspect(error)

    console.rule("[bold cyan]Ansible Lint completed.")


if __name__ == "__main__":
    main()
