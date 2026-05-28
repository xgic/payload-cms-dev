"""Run Ansible playbooks with the Ansible Python API."""
import sys

from ansible.cli.playbook import PlaybookCLI


def main() -> None:
    """Main function.

    Creates a playbook CLI object with commandline parameters and runs it.
    """
    cli = PlaybookCLI(sys.argv)
    cli.run()


if __name__ == "__main__":
    main()
