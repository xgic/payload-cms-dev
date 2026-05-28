"""Run Ansible test playbooks with the Ansible Python API."""
import os
import pty
import select
import subprocess
import sys
import time


def main() -> None:
    """Main function.

    1. Creates a playbook CLI object with commandline parameters and runs it.
    2. Runs Ansible Lint.
    """
    playbook: str = sys.argv[1]

    # Define the command to run the Ansible Playbook
    command = ["ansible-playbook", playbook]
    delay_count = 0
    subprocess.call("reset")

    # Open a new pseudo-terminal pair
    master, slave = pty.openpty()

    # Spawn a new process and connect its controlling terminal with the current
    # process's standard io
    process = subprocess.Popen(
        command,
        # shell=True,
        stdin=subprocess.PIPE,
        stdout=slave,
        stderr=subprocess.STDOUT,
    )

    # Loop copies STDIN of the current process to the child and data received from
    # the child to STDOUT of the current process
    while True:
        try:
            # Check if data is available to be read from the file descriptor
            if select.select([master], [], [], 0)[0]:
                output = os.read(master, 1024)
                if not output:
                    break
                print(output.decode(), end="")
            else:
                time.sleep(1)
                delay_count += 1
                if delay_count > 2:
                    break

        except KeyboardInterrupt:
            break

    # Close the file descriptors
    os.close(master)
    os.close(slave)


if __name__ == "__main__":
    main()
