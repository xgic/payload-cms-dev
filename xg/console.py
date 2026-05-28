"""XG Console Automation Control Module

This module defines the XG console automation control arguments and subcommands.
Additionally, some of the classes in this module can be instantiated in other
modules to reuse functionality.
"""

import argparse
import os
import subprocess
import sys
from enum import Enum
from typing import Any

from xg import util
from xg.api.ansible.playbook.debug import XGPlaybookDebugger
from xg.api.docker import compose

# from xg.api import gitlab
# from xg.api import gitlab


class XGAppEnv(str, Enum):
    """Defines the valid environments for XG applications."""

    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class BaseApp:
    """This class defines shared base methods and attributes."""

    def __init__(self, app_env: str | None = None) -> None:
        # Instance variables
        self.ansible_key_ring_client: str
        self.app_dir: str
        self.app_env: str
        self.docker_compose_dir: str
        self.docker_compose_file: str
        self.home_dir: str
        self.is_in_docker_container: bool = self.__is_in_docker()

        # Set the default initial environment. However, the environment can be
        # also updated at runtime with XG console command arguments.
        if app_env:
            self.app_env = app_env
        elif os.environ.get("XG_AIS_ENV"):
            self.app_env = str(os.environ.get("XG_AIS_ENV"))

    def docker_system_prune(self) -> None:
        """Runs docker system prune including volumes to remove unused
        artifacts.
        """
        script: str = """
            printf "\ndocker system prune --volumes\n\n"
            docker system prune --volumes -f
            """
        print("\n\nRunning docker system prune to remove unused artifacts.\n")
        self.run_script(script)
        self.print_docker_status()

    def __is_in_docker(self) -> bool:
        """Checks if this application is running in a Docker container.

        Returns:
            bool: Returns True if this application is running in a Docker
            container or False if it's running in any other platform.
        """
        dockerenv_file: str = "/.dockerenv"
        if (
            os.path.isfile(dockerenv_file)
            and os.path.islink(dockerenv_file) is False
        ):
            return True

        return False

    def print_docker_status(
        self, docker_compose_command_prefix: str = ""
    ) -> None:
        """Prints the status of Docker and Docker Compose services.

        Args:
            docker_compose_command_prefix (str, optional): A valid docker
            compose command prefix which includes all of the required
            configuration file paths.
        """
        docker_compose_ps: str = ""

        if docker_compose_command_prefix:
            docker_compose_ps = f"""
                printf "\n\n{docker_compose_command_prefix} ps -a\n\n"
                {docker_compose_command_prefix} ps -a
                """
        script: str = f"""
            printf "docker compose ls\n\n"
            docker compose ls

            {docker_compose_ps}

            printf "\n\ndocker ps -as\n\n"
            docker ps -as

            printf "\n\ndocker images\n\n"
            docker images

            printf "\n\ndocker volume ls\n\n"
            docker volume ls

            printf "\n\ndocker network ls\n\n"
            docker network ls
            """
        print("\n\nXG AIS Docker Status:\n")
        self.run_script(script)
        print()

    def print_environment_variables(self, env_var=None) -> None:
        """Prints environment variables.

        Args:
            env_var (optional): A single environment variable or none to
            print all current variables. Defaults to None.
        """
        script: str

        if env_var:
            script = f'echo "{env_var} = ${env_var}"'
        else:
            script = "env"

        self.run_script(script)

    def run_docker_command(self, command: str) -> subprocess.CompletedProcess:
        """Run Docker commands using Python.

        TODO(xoren): Create an alternate version of this function using the
        Python API.

        Args:
            command (str): Docker command and arguments.

        Returns:
            subprocess.CompletedProcess: An instance of CompletedProcess class.
        """
        output: subprocess.CompletedProcess

        try:
            output = subprocess.run(
                ["bash", "-c", command],
                capture_output=True,
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            print(f"STDOUT: {error.stdout}\n")
            print(f"STDERR: {error.stderr}\n")
            print(f"RETURN_CODE: {error.returncode}\n")
            raise subprocess.CalledProcessError(
                returncode=error.returncode, cmd="bash"
            ) from error

        return output

    def run_script(
        self, script: str, verbose: bool = False
    ) -> subprocess.CompletedProcess:
        """Run Bash scripts using Python.

        Args:
            script (str): Bash script
            verbose (bool): True for verbose messages, defaults to False.

        Returns:
            subprocess.CompletedProcess: An instance of CompletedProcess class.

        Exceptions:
            subprocess.CalledProcessError
        """
        output: subprocess.CompletedProcess

        try:
            output = subprocess.run(
                ["bash", "-c", script],
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            if verbose:
                print(f"\nSTDOUT: {error.stdout}\n")
                print(f"STDERR: {error.stderr}\n")
                print(f"RETURN_CODE: {error.returncode}\n")
                raise

            output = subprocess.CompletedProcess("bash", returncode=1)
            sys.exit()

        except KeyboardInterrupt as error:
            print(f"\nExiting script ({error}).\n")
            output = subprocess.CompletedProcess("bash", returncode=0)

        return output


class XG(BaseApp):
    """This class defines the Xoren Games Control Application."""

    def __init__(self) -> None:
        """Initialize XG class."""
        super().__init__()

        parser = self.get_argument_parser()
        args = parser.parse_args()

        try:
            args.func(args)
        except:
            self.debug_args(args)
            raise

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds XG required and optional arguments.

        Args:
            parser (ArgumentParser): An instance of the ArgumentParser class
        """
        subparsers = parser.add_subparsers(
            title="Specify which application to control (required)",
            help="Control the specified application.",
        )
        self.add_arguments_ais(subparsers)
        self.add_arguments_gitlab(subparsers)
        self.add_arguments_cms(subparsers)

    def add_arguments_ais(self, subparsers) -> None:
        """Adds XG AIS arguments.

        Args:
            subparsers: A subparsers instance to enable adding subcommands.
        """
        # Adding AIS options
        ais_parser = subparsers.add_parser(
            "ais",
            description=(
                "Using this command with no options starts an interactive Bash "
                "shell session on the XG AIS controller node (same as option "
                "-b). All options are mutually exclusive, except for the -v "
                "(verbose) option."
            ),
            help="XG AIS application",
        )
        ais_required_arg_group = ais_parser.add_argument_group(
            "required arguments"
        )
        ais_required_arg_group.add_argument(
            "environment",
            choices=["dev", "prod", "test"],
            help="An XG AIS application environment.",
        )
        ais_parser.add_argument(
            "-v",
            "--verbose",
            help="Increases verbosity level of messages.",
            action="store_true",
        )

        # Mutually exclusive group
        exclusive_group = ais_parser.add_mutually_exclusive_group()
        self.add_arguments_ais_bash_shell(exclusive_group)
        self.add_arguments_ais_docker_status(exclusive_group)
        self.add_arguments_ais_edit_vars(exclusive_group)
        self.add_arguments_ais_playbook_main(exclusive_group)
        self.add_arguments_ais_docker_system_prune(exclusive_group)
        self.add_arguments_ais_restart_services(exclusive_group)
        self.add_arguments_ais_stop_services(exclusive_group)
        self.add_arguments_ais_playbook_test(exclusive_group)

        # Set defaults
        ais = AIS()
        exclusive_group.set_defaults(func=ais.process_args)

    def add_arguments_ais_bash_shell(self, arg_group: Any) -> None:
        """Adds XG AIS Bash Only argument.

        Args:
            arg_group (Any): A mutually exclusive argument group instance.
        """
        arg_group.add_argument(
            "-b",
            "--bash-shell",
            help="""
                Start Bash interactive shell session.
                """,
            action="store_true",
        )

    def add_arguments_ais_docker_status(self, arg_group: Any) -> None:
        """Adds Docker Compose status  argument.

        Args:
            arg_group (Any): A mutually exclusive argument group instance.
        """
        arg_group.add_argument(
            "-d",
            "--docker-status",
            help="Print Docker and Docker Compose status information.",
            action="store_true",
        )

    def add_arguments_ais_docker_system_prune(self, arg_group: Any) -> None:
        """Adds Docker Compose system prune argument.

        Args:
            arg_group (Any): A mutually exclusive argument group instance.
        """
        arg_group.add_argument(
            "-p",
            "--docker-prune",
            help=(
                "Runs docker system prune including volumes to remove unused "
                "artifacts."
            ),
            action="store_true",
        )

    def add_arguments_ais_edit_vars(self, arg_group: Any) -> None:
        """Edits group var files for the specified environment.

        Args:
            arg_group (Any): A mutually exclusive argument group instance.
        """
        arg_group.add_argument(
            "-e",
            "--edit-vars",
            help=(
                "Edit Ansible Vault encrypted main group variable files for "
                "the specified environment."
            ),
            action="store_true",
        )

    def add_arguments_ais_playbook_main(self, arg_group: Any) -> None:
        """Adds XG AIS Main Playbook argument.

        Args:
            arg_group (Any): A mutually exclusive argument group instance.
        """
        arg_group.add_argument(
            "-m",
            "--main-playbook",
            help="""
                Run main Ansible playbook.
                """,
            action="store_true",
        )

    def add_arguments_ais_playbook_test(self, arg_group: Any) -> None:
        """Adds XG AIS Test Playbook argument.

        Args:
            arg_group (Any): A mutually exclusive argument group instance.
        """
        arg_group.add_argument(
            "-t",
            "--test-playbook",
            help="""
                Run test Ansible playbook.
                """,
            action="store_true",
        )

    def add_arguments_ais_restart_services(self, arg_group: Any) -> None:
        """Adds XG AIS Restart Services argument.

        Args:
            arg_group (Any): A mutually exclusive argument group instance.
        """
        arg_group.add_argument(
            "-r",
            "--restart",
            help=(
                "Starts or restarts all XG AIS Docker Compose services for the "
                "specified environment."
            ),
            action="store_true",
        )

    def add_arguments_ais_stop_services(self, arg_group: Any) -> None:
        """Adds XG AIS Stop Services argument.

        Args:
            arg_group (Any): A mutually exclusive argument group instance.
        """
        arg_group.add_argument(
            "-s",
            "--stop",
            help="""
                Stops all XG AIS Docker Compose services.
                """,
            action="store_true",
        )

    def add_arguments_gitlab(self, subparsers) -> None:
        """Adds XG GitLab arguments.

        Args:
            subparsers: A subparsers instance to enable adding subcommands.
        """
        # Adding GitLab options
        gitlab_parser = subparsers.add_parser(
            "gitlab", help="XG GitLab application"
        )

        # Mutually exclusive group
        gitlab_group = gitlab_parser.add_mutually_exclusive_group()
        gitlab_group.add_argument(
            # gitlab_parser.add_argument(
            "--create-project",
            nargs=2,
            metavar=("<project>", "<type>"),
            help="""
                Create GitLab projects.
                """,
        )

        # Set defaults
        # xg_gitlab = gitlab.RestAPI()
        # gitlab_group.set_defaults(func=xg_gitlab.create_project)

    def add_arguments_cms(self, subparsers) -> None:
        """Adds XGCMS arguments.

        Args:
            subparsers: A subparsers instance to enable adding subcommands.
        """
        # Adding XGCMS options
        cms_parser = subparsers.add_parser("cms", help="XGCMS application")

        # Mutually exclusive group
        # cms_group = cms_parser.add_mutually_exclusive_group()
        # cms_group.add_argument(
        cms_parser.add_argument(
            "command",
            choices=["start", "stop"],
            help="XGCMS control commands",
        )

    def debug_args(self, args: argparse.Namespace) -> None:
        """Prints the args object for debugging.

        Args:
            args (Sequence): An Argparse argument sequence.
        """
        print(f"\n\nargs = {args}\n\n")

    def get_argument_parser(self) -> argparse.ArgumentParser:
        """Instantiates the ArgumentParser class.

        Returns:
           (ArgumentParser) An instance of the ArgumentParser class
        """
        parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description="Controls Xoren Games applications."
        )

        self.add_arguments(parser)

        return parser


class AIS(BaseApp):
    """This class defines all the commands for controlling XG AIS."""

    def __init__(self, app_env: str | None = None) -> None:
        """Initialize AIS class."""
        super().__init__(app_env=app_env)
        self.ansible_key_ring_client = (
            "xg_ais_vault_id@/usr/local/bin/xg-ais-keyring-client"
        )
        self.home_dir = os.path.expanduser("~")
        self.app_dir = f"{self.home_dir}/source/xg-ais"
        self.verbose: bool = False
        self.xg_ais_container: str

    def edit_group_vars(self) -> None:
        """Edit the Ansible Vault encrypted main group variable file."""
        script: str
        docker_cmd: str
        vault_filepath: str = self.get_group_vars_all_filepath()
        ansible_cmd: str

        if self.get_is_in_control_node_container():
            ansible_cmd = f"ansible-vault edit {vault_filepath}"
            self.run_script(ansible_cmd)
        else:
            docker_cmd = self.get_docker_exec_command_prefix_dev()
            ansible_cmd = f"xg ais {self.app_env} -e"
            script = f"{docker_cmd} {ansible_cmd}"
            self.run_script(script)

    def get_docker_compose_command_prefix(self) -> str:
        """Gets the Docker Compose command prefix for the current environment.

        Raises:
            ValueError: Invalid environment argument exception.

        Returns:
            str: A Docker Compose command prefix.
        """
        self.docker_compose_dir = f"{self.app_dir}"
        docker_compose_cmd: str = ""

        if self.app_env == "prod":
            self.docker_compose_file = "docker-compose.yml"
            docker_compose_cmd = (
                "docker compose"
                f" -f {self.docker_compose_dir}/{self.docker_compose_file}"
            )
        elif self.app_env == "dev":
            self.docker_compose_file = ".devcontainer/docker-compose-dev.yml"
            docker_compose_cmd = (
                "docker compose"
                f" -f {self.docker_compose_dir}/{self.docker_compose_file}"
            )
        elif self.app_env == "test":
            self.docker_compose_file = ".testcontainer/docker-compose-test.yml"
            docker_compose_cmd = (
                "docker compose"
                f" -f {self.docker_compose_dir}/{self.docker_compose_file}"
            )
        else:
            raise ValueError("Invalid environment.")

        return (
            f"{docker_compose_cmd} -p {self.get_docker_compose_project_name()}"
        )

    def get_docker_compose_project_name(self) -> str:
        """Gets the Docker Compose project name for the current environment.

        Returns:
            str: A Docker Compose project name.
        """
        xg_ais_project: str = next(
            (
                p
                for p in compose.get_running_project_names()
                if p.startswith(f"xg-ais_{self.app_env}")
            ),
            f"xg-ais-{self.app_env}",
        )
        return xg_ais_project

    def get_docker_exec_command_prefix(self) -> str:
        """Gets the Docker execute command prefix.

        Returns:
            str: A Docker execute command prefix.
        """
        return f"docker exec -it {self.xg_ais_container}"

    def get_docker_exec_command_prefix_dev(self) -> str:
        """Gets the Docker execute command prefix for the development
        environment.

        Returns:
            str: A Docker execute command prefix.
        """
        return "docker exec -it xg-ais-dev"

    def get_group_vars_all_filepath(self) -> str:
        """Gets the group vars all filepath for the specified environment.

        Returns:
            str: A group vars all filepath.
        """
        inventory_dir: str = self.get_inventory_directory()
        vault_filepath: str = os.path.join(
            inventory_dir, "group_vars/all/vault.yml"
        )

        return vault_filepath

    def get_inventory_directory(self) -> str:
        """Gets the full path to the inventory directory for the specified
         environment.

        Returns:
            str: Full path to the inventory directory.
        """
        target_env: str = self.get_environment()
        inventory_dir: str = os.path.join(
            util.ANSIBLE_INVENTORIES_DIR, target_env
        )

        return inventory_dir

    def get_is_in_control_node_container(self) -> bool:
        """Checks if this application is running in an Ansible controller node
        container.

        Returns:
            bool: Returns true if the application is running in an Ansible
            controller node container.
        """
        if (
            self.is_in_docker_container
            and os.environ["XG_AIS_HOST_TYPE"] == "control_node"
        ):
            return True
        else:
            return False

    def get_environment(self) -> str:
        """Gets the specified environment name or raises a ValueError exception
        if an invalid environment is requested.

        Raises:
            ValueError: Invalid environment argument exception.

        Returns:
            str: A valid XG AIS environment name.
        """
        target_env: str
        environment: str = self.app_env

        if environment in ["dev", "test"]:
            target_env = "development"
        elif environment == "prod":
            target_env = "production"
        else:
            raise ValueError("Invalid environment argument.")

        return target_env

    def process_args(self, app_args) -> None:
        """Processes arguments passed from main XG module.

        Args:
            app_args: Commandline arguments.
        """
        # Required arguments
        self.app_env = app_args.environment
        self.xg_ais_container = f"xg-ais-{self.app_env}"

        # Optional arguments
        if app_args.verbose:
            self.verbose = True

        # Mutually exclusive arguments.
        if app_args.bash_shell:
            self.start_shell_on_ansible_control_node()
        elif app_args.docker_status:
            self.print_docker_status(self.get_docker_compose_command_prefix())
        elif app_args.docker_prune:
            self.docker_system_prune()
        elif app_args.edit_vars:
            self.edit_group_vars()
        elif app_args.main_playbook:
            self.run_ansible_playbook_main()
        elif app_args.restart:
            self.rebuild_and_start_docker_compose_services()
        elif app_args.stop:
            self.stop_xg_ais_docker_compose_services()
        elif app_args.test_playbook:
            self.run_ansible_playbook_test()
        else:
            self.start_shell_on_ansible_control_node()

    def rebuild_and_start_docker_compose_services(self) -> None:
        """Rebuilds XG AIS and starts all services for the specified
        environment.
        """
        docker_compose_cmd_prefix: str = (
            self.get_docker_compose_command_prefix()
        )
        docker_compose_build_cmd: str = (
            f"{docker_compose_cmd_prefix} build --progress plain"
        )
        script: str

        print("\n\nStarting full build of XG AIS Docker Compose services\n")

        # Run script to stop and remove containers.
        script = f"""
            printf '\n{docker_compose_cmd_prefix} down\n\n'
            {docker_compose_cmd_prefix} down
        """
        self.print_docker_status(docker_compose_cmd_prefix)
        self.run_script(script, self.verbose)

        # Run build and restart script.
        script = f"""
            printf '\n\n{docker_compose_build_cmd}\n\n'
            {docker_compose_build_cmd}
            printf '\n\n{docker_compose_cmd_prefix} up -d\n\n'
            {docker_compose_cmd_prefix} up -d
        """
        self.run_script(script, self.verbose)
        self.print_docker_status(docker_compose_cmd_prefix)

        print("\nCompleted full build of XG AIS Docker Compose services\n")

    def run_ansible_playbook(self, script: str) -> None:
        """Run a XG AIS Ansible playbook.

        Args:
            script (str): Bash script
        """
        try:
            self.run_script(script, self.verbose)
        except subprocess.CalledProcessError as error:
            if error.returncode == 4:
                print(
                    f"\nWarning: {util.inner_trim(script)} command "
                    f"return code {error.returncode}\n"
                )
            else:
                raise

    def run_ansible_playbook_main(self) -> None:
        """Run the main XG AIS Ansible playbook."""
        script: str
        docker_cmd: str = ""
        verbose: str = "-vvv" if self.verbose else ""
        xg_playbook_debugger: XGPlaybookDebugger = XGPlaybookDebugger(
            playbook_filepath=util.ANSIBLE_PLAYBOOK_MAIN
        )

        if self.get_is_in_control_node_container():
            xg_playbook_debugger.run()
        else:
            xg_ansible_debugger_cmd: str = f"xg ais {self.app_env} -m"
            docker_cmd = self.get_docker_exec_command_prefix()
            script = f"{docker_cmd} {xg_ansible_debugger_cmd} {verbose}"

            print("\n\nStarting run of our main XG AIS Ansible playbook.\n\n")
            self.run_ansible_playbook(script)
            print("\n\nCompleted run of our main XG AIS Ansible playbook.\n\n")

    def run_ansible_playbook_test(self) -> None:
        """Run the test XG AIS Ansible playbook."""
        script: str
        docker_cmd: str = ""
        verbose: str = "-vvv" if self.verbose else ""
        xg_playbook_debugger: XGPlaybookDebugger = XGPlaybookDebugger(
            playbook_filepath=util.ANSIBLE_PLAYBOOK_TEST
        )

        if self.get_is_in_control_node_container():
            xg_playbook_debugger.run()
        else:
            xg_ansible_debugger_cmd: str = f"xg ais {self.app_env} -t"
            docker_cmd = self.get_docker_exec_command_prefix()
            script = f"{docker_cmd} {xg_ansible_debugger_cmd} {verbose}"

            print("\n\nStarting run of our test XG AIS Ansible playbook.\n\n")
            self.run_ansible_playbook(script)
            print("\n\nCompleted run of our test XG AIS Ansible playbook.\n\n")

    def run_pytest_on_ansible_control_node(
        self, pytest_command: str = "pytest"
    ) -> None:
        """Runs pytest on the test environments Ansible Control Node.

        Args:
            pytest_command (str, optional): A pytest command to run. Defaults
            to "pytest".
        """
        self.app_env = XGAppEnv.TEST.value
        self.rebuild_and_start_docker_compose_services()

        # TODO(xoren): Fix - not showing test output.
        # docker_command = (
        #   f"docker exec {self.xg_ais_container} {pytest_command}\"
        docker_command = f"docker exec -it {self.xg_ais_container} bash"
        print(f"\n{docker_command}\n")
        self.run_docker_command(docker_command)

        self.stop_xg_ais_docker_compose_services()

    def run_test_ansible_playbook(self) -> None:
        """Run the test XG AIS Ansible playbook."""
        docker_compose_cmd: str = self.get_docker_compose_command_prefix()
        script: str = (
            f"{docker_compose_cmd} \\"
            f"exec {self.xg_ais_container} ansible-playbook ansible/test.yml"
        )

        print("\n\nStarting run of our test XG AIS Ansible playbook.\n\n")
        self.run_ansible_playbook(script)
        print("\n\nCompleted run of our test XG AIS Ansible playbook.\n\n")

    def exit_if_running_in_docker(self, message: str = "") -> None:
        """Returns if this application is running in a Docker container."""
        if self.__is_in_docker():
            if message == "":
                print("Unable to continue while running in Docker container.")
            else:
                print(message)
            sys.exit(0)

    def start_shell_on_ansible_control_node(self) -> None:
        """Starts an interactive Bash shell on the XG AIS Ansible
        Docker Compose service control node container.
        """
        script = f"docker exec -it {self.xg_ais_container} bash"

        print(
            "\n\nStarting interactive Bash shell on XG AIS Ansible control "
            "node.\n"
        )

        self.run_script(script, self.verbose)

        print(
            "\nClosed interactive Bash shell on XG AIS Ansible control"
            "node.\n\n"
        )

    def stop_xg_ais_docker_compose_services(self) -> None:
        """Stops all XG AIS Docker Compose services."""
        project_name: str = self.get_docker_compose_project_name()
        script: str = f"docker compose -p {project_name} down"

        print("\n\nStopping all XG AIS Docker Compose services.\n\n")
        print(f"{script}\n")

        self.run_script(script, self.verbose)
        self.print_docker_status()

        print("\n\nStopped all XG AIS Docker Compose services.\n\n")
