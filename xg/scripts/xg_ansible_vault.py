"Testing Ansible vault command with subprocess.Popen class."
import ast
import json
import os
import subprocess
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Any, Dict, List

from rich import inspect
from rich.console import Console
from rich.panel import Panel

console = Console()
SUBPROCESS_URL = "https://docs.python.org/3/library/subprocess.htm"


def run_ansible_vault_view_command(encrypted_file_path: Path) -> Dict[str, Any]:
    """Runs the Ansible vault command to view encrypted files.

    Args:
        encrypted_file_path (Path): An Ansible vault encrypted file path.

    Returns:
        Dict[str, Any]: A dictionary containing the process return values of
        return code, stdout and stderr.
    """
    args: List[str] = ["ansible-vault", "view", str(encrypted_file_path)]
    return run_command(args=args)


def run_command(args: List[str], timeout: float = 15) -> Dict[str, Any]:
    """Runs a command subprocess using the specified arguments.

    Args:
        args (List[str]): A list of arguments. The first argument must be the
        executable program or command.
        timeout (float): The process timeout in seconds. If the process timeout
        expires a subprocess.TimeoutExpired exception occurs.

    Raises:
        RuntimeError: If any errors occurred while running the subprocess.

    Returns:
        Dict[str, Any]: A dictionary containing the process return values of
        return code, stdout and stderr.
    """
    # Set output defaults
    stderr: str = ""
    stdout: str = ""
    return_code: Any = None
    timeout = 15
    output: Dict[str, Any] = {
        "return_code": None,
        "stdout": None,
        "stderr": None,
    }

    # Execute the child program in a new process and store the return values.
    with subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except TimeoutExpired as error:
            process.kill()
            raise RuntimeError(
                f"TimeoutExpired ({error}) running command {args}, "
                f"output=[{output}]."
            ) from TimeoutExpired
        except OSError as error:
            raise RuntimeError(
                f"OSError ({error}) running command {args}, output=[{output}]."
            ) from OSError
        except Exception as error:
            raise RuntimeError(
                f"Error ({error}) running command {args}, output=[{output}]."
            ) from Exception
        finally:
            stdout, stderr = process.communicate()
            return_code = process.returncode
            output = {
                "return_code": return_code,
                "stderr": stderr,
                "stdout": stdout,
            }

    return output


console.print(
    Panel(
        f"Starting {os.path.realpath(__file__)}",
        title="Testing Ansible View Command",
        subtitle=f"Using Python subprocess.Popen class ({SUBPROCESS_URL})",
        style=("bold black on cyan"),
    )
)

encrypted_file: Path = Path(
    "ansible/roles/gitlab/files/vault/6ac1a0e6-a327-545d-8964-c338764b36e0.le1"
)
if not encrypted_file.exists():
    raise FileNotFoundError(f"File '{encrypted_file}' does not exists.")

console.rule("[bold cyan]Inspecting Ansible Vault command result.")
result = run_ansible_vault_view_command(encrypted_file_path=encrypted_file)
inspect(result, methods=True)

console.rule(
    f"[bold cyan]Raw output form Ansible (length={len(result['stdout'])})."
)
console.print(result["stdout"], no_wrap=True)

console.rule("[bold cyan]Converting Ansible output to dictionary.")
output_dict: Dict[str, Any] = ast.literal_eval(result["stdout"])
console.print(output_dict)

console.rule("[bold cyan]Converting dictionary back to JSON.")
output_json = json.JSONEncoder().encode(output_dict)
inspect(output_json, methods=True)

console.rule("[bold cyan]Pretty printing JSON with Rich library.")
console.print_json(json=output_json)

console.rule("[bold cyan]Getting values from dictionary output.")
console.print(output_dict["mailroom"])
