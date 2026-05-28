import datetime
import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def display_file(file_name):
    console = Console()
    with open(file_name, "r") as file:
        file_content = file.read()
    header = Panel(file_name, title="Header Pane")
    footer = Panel(
        Text(
            f"[b]Current Date:[/b] {datetime.datetime.now().strftime('%Y-%m-%d')} [b]Current Time:[/b] {datetime.datetime.now().strftime('%H:%M:%S')} [b]Keyboard Shortcuts:[/b] [u]R[/u] for reloading, [u]Esc[/u] for exiting the program."
        ),
        title="Footer Pane",
    )
    console.print(header)
    console.print(file_content)
    console.print(footer)


if __name__ == "__main__":
    FILE_NAME = "/home/xg-ais/source/xg-ais/tests/ansible/playbooks/test_roles_gitlab_tasks_migration_site_ssh_keys.yml"

    subprocess.call("reset")

    display_file(FILE_NAME)
