"""Run Ansible test playbooks with the Ansible Python API."""
import fcntl
import os
import pty
import re
import select
import struct
import subprocess
import sys
import termios
import time
from subprocess import TimeoutExpired
from typing import List

from ansible.cli.playbook import PlaybookCLI
from rich import inspect
from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    """Main function.

    1. Creates a playbook CLI object with commandline parameters and runs it.
    2. Runs Ansible Lint.
    """
    playbook: str = sys.argv[1]

    subprocess.call("reset")

    # Header
    console.print(
        Panel(
            f"Starting {os.path.realpath(__file__)}",
            title="Testing Ansible Playbook",
            subtitle=f"{playbook})",
            style=("bold black on cyan"),
        )
    )

    # Start playbook process
    command = ["ansible-playbook", playbook]
    master, slave = pty.openpty()

    # # Set terminal width
    # env = os.environ.copy()
    # terminal_rows, terminal_columns = os.get_terminal_size()
    # env["ROWS"] = str(terminal_rows)
    # env["COLUMNS"] = str(terminal_columns)
    # # console.print(env)

    # Get the size of the parent terminal window
    size = struct.pack("HHHH", 0, 0, 0, 0)
    size = fcntl.ioctl(0, termios.TIOCGWINSZ, size)
    rows, cols, xpixels, ypixels = struct.unpack("HHHH", size)

    # Set the size of the slave file descriptor
    fcntl.ioctl(slave, termios.TIOCSWINSZ, size)

    with subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=slave,
        stderr=subprocess.STDOUT,
        # env=env,
    ) as process:
        output = b""
        subprocess.call("reset")

        while True:
            try:
                if select.select([master], [], [], 0)[0]:
                    output = os.read(master, 1024)
                    if not output:
                        break
                    print(output.decode("utf-8"), end="")
                else:
                    time.sleep(0.5)
            except OSError:
                console.print_exception()
            except KeyboardInterrupt:
                break

    os.close(master)
    os.close(slave)

    # process.wait()

    # # Get include Ansible task paths

    # # Causes error (“/bin/sh: 1: history: not found”)
    # # output = subprocess.check_output(["history"], shell=True)

    # output = subprocess.check_output(["bash", "-c", "history"], shell=False)

    # output_str = output.decode("utf-8")

    # console.rule("[bold cyan]Running Ansible Lint.")
    # console.print(output_str)
    # # args = ["ansible-lint", playbook]
    # # args.append()
    # # try:
    # #     subprocess.run(args, capture_output=False, check=True)
    # # except subprocess.CalledProcessError as error:
    # #     console.print(f"RETURN_CODE: {error.returncode}\n")
    # #     # inspect(error)

    # console.rule("[bold cyan]Ansible Lint completed.")


if __name__ == "__main__":
    main()
