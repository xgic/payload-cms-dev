"""XG Utilities Module

This module defines shared utility functions.
"""

import base64
import os
import re
import subprocess
import uuid
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from stat import S_IREAD
from subprocess import TimeoutExpired
from typing import Annotated, Any, Dict, List

import requests
import rich
from packaging import version
from pydantic import (
    BaseModel,
    FilePath,
    StrictBool,
    StringConstraints,
    validate_call,
)

# Constants
HOME_DIR: FilePath = Path.home()
SOURCE_DIR: FilePath = HOME_DIR.joinpath("source")
APP_DIR: FilePath = SOURCE_DIR.joinpath("xg-ais")
ANSIBLE_DIR: FilePath = APP_DIR.joinpath("ansible")
ANSIBLE_INVENTORIES_DIR: FilePath = ANSIBLE_DIR.joinpath("inventories")
ANSIBLE_PLAYBOOK_MAIN: FilePath = ANSIBLE_DIR.joinpath("xg_ais.yml")
ANSIBLE_PLAYBOOK_TEST: FilePath = ANSIBLE_DIR.joinpath("test.yml")
TESTS_DIR: FilePath = APP_DIR.joinpath("tests")
TEST_HOST_CONTAINER: str = "xg-ais-test"
CURRENT_ENVIRONMENT: str | None = os.environ.get("XG_AIS_ENV")
XG_AIS_HOST_TYPE: str | None = os.environ.get("XG_AIS_HOST_TYPE")

# Regular expression validation patterns
ANSIBLE_HOST_PATTERN = r"^[a-zA-Z_-][a-zA-Z0-9__-]*$"
ANSIBLE_MODULE_PATTERN = r"^[a-zA-Z][a-zA-Z0-9\.__-]*$"
ANSIBLE_PLAYBOOK_FILENAME_PATTERN = r"^[a-zA-Z0-9_-]+\.yml$"
ANSIBLE_VARIABLE_PATTERN = r"^[a-zA-Z_][a-zA-Z0-9__]*$"
EXECUTABLE_PATTERN = r"^[a-zA-Z][a-zA-Z0-9\.__-]*$"


class XGDuration(BaseModel):
    """A class to store start and end times and calculate duration.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    start: datetime
    end: datetime | None = None


class XGStatus(str, Enum):
    """An enumeration class to indicate status.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    ERROR = "error"  # One or more errors occurred.
    SUCCESS = "success"  # No errors or warnings occurred.
    WARNING = "warning"  # One or more warnings occurred.


@validate_call
def append_to_file(file_path: Path, text_to_append: str) -> None:
    """Appends text to the end of a file.

    Args:
        file_path (Path): Full path to the target file.
        text_to_append (str): Text to append to the end of the file.
    """
    with file_path.open(mode="a", encoding="utf-8") as file:
        file.write(f"{text_to_append}\n")


@validate_call
def create_blank_file(file_path: Path) -> None:
    """Creates a blank file at the specified path.

    Args:
        file_path (Path): Full path for the file to be created.
    """
    file_path.touch(exist_ok=False)


@validate_call
def create_directories(
    full_path: Path,
    exists_ok: StrictBool = True,
    mode: int = 511,
    parents: StrictBool = True,
) -> None:
    """Recursively creates directories.

    Args:
        full_path (Path): A full path, which can include any number
        of non-existing intermediate directories.
        exists_ok (bool, optional): If exists_ok is False, a FileExistsError is
        raised if the target directory already exists. Defaults to True.
        mode (int, optional): If mode is given, it's combined with the process’
        umask value to determine the file mode and access flags. Defaults to
        511 (0o777).
        parents (bool, optional): If parents is false, a missing parent raises
        FileNotFoundError. Defaults to True.
    """
    full_path.mkdir(mode=mode, parents=parents, exist_ok=exists_ok)


@validate_call
def base64_encode(
    encode_text: Annotated[str, StringConstraints(min_length=1)],
) -> str:
    """Encodes a string using base64.

    Args:
        encode_text (str): A string to encode with a minimum 1 character in
        length.

    Returns:
        str: A base64 utf-8 encoded string
    """
    encode_bytes = encode_text.encode("utf-8")
    base64_bytes = base64.b64encode(encode_bytes)
    return str(base64_bytes)


@validate_call
def get_ansible_variable(
    ansible_var: Annotated[
        str, StringConstraints(min_length=1, pattern=ANSIBLE_VARIABLE_PATTERN)
    ],
    host: Annotated[
        str, StringConstraints(min_length=3, pattern=ANSIBLE_HOST_PATTERN)
    ] = "localhost",
    extra_vars: str = "",
) -> subprocess.CompletedProcess:
    """Runs an Ansible CLI command using the specified parameters.

    Args:
        ansible_var (str): An Ansible variable with a minimum length of
        1 character.
        host (str): An Ansible host with a minimal length of 3 characters.
        Defaults to localhost.
        extra_vars (str, optional): Set additional variables as key=value or
        YAML/JSON, if filename prepend with @. This argument may be specified
        multiple times. Defaults to "" (empty string).

    Returns:
        subprocess.CompletedProcess: An instance of CompletedProcess class.
    """
    return run_ansible_command(
        host=host,
        module="ansible.builtin.debug",
        module_args="".join(['var="{{', f" '{ansible_var}' ", '}}"']),
        extra_vars=extra_vars,
    )


@validate_call
def get_current_date_and_time(
    datetime_format: Annotated[
        str, StringConstraints(min_length=2)
    ] = "%Y-%m-%d %H:%M",
) -> str:
    """Gets the current date and time in the specified format.

    Args:
        datetime_format (str, optional): A date time format string with a
        minimal length of 2 characters. Defaults to "%Y-%m-%d %H:%M".

    Returns:
        str: A date and time string in the specified format. Defaults to the
        format yyyy-mm-dd hh:mm (e.g. 2024-01-16 21:31) if not specified.
    """
    now = datetime.now()
    return now.strftime(datetime_format)


@validate_call
def get_latest_stable_python_version(
    verbose: StrictBool = False,
) -> version.Version:
    """Gets the latest stable Python semantic version from GitHub.

    Args:
        verbose (bool, optional): Print verbose output if true. Defaults to
        False.

    Raises:
        ValueError: Latest stable Python semantic version not found.

    Returns:
        packaging.version.Version: Latest stable Python semantic Version
        instance.
    """

    url = "https://api.github.com/repos/python/cpython/tags"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers, stream=True, timeout=60)
    response = response.json()
    latest_version: str = ""
    sorted_python_tags = sorted(
        response,
        key=lambda d: d["name"],
        reverse=True,
    )
    version_count = len(sorted_python_tags)

    if verbose:
        print(
            "".join(
                f"\nThese are the last { version_count } tags in the Python "
                "GitHub repository."
            )
        )
        print(f"\n{sorted_python_tags}\n")

    for tag in sorted_python_tags:
        python_tag = tag["name"]
        patch_version = re.split(r"[-.]", python_tag)[-1]

        if str(patch_version).isdigit():
            latest_version = python_tag[1:]
            if validate_semantic_version_number(latest_version):
                if verbose:
                    print(
                        "".join(
                            "The latest stable Python semantic version is"
                            f" [{latest_version}]"
                        )
                    )
                break

    if latest_version == "":
        raise ValueError("Latest stable Python semantic version not found.")

    return version.parse(latest_version)


@validate_call
def get_uuid_filename(extension: str = "") -> str:
    """Gets a UUID filename.

    Args:
        extension (str, optional): An optional file extension. Defaults to "".

    Returns:
        str: A UUID filename and optional extension.
    """

    if extension != "":
        extension = f".{extension}"
    return f"{uuid.uuid4()}{extension}"


@validate_call
def inner_trim(str_var: str) -> str:
    """Removes extra spaces and lines replacing them with a single space.

    Args:
        str_var (str): A string instance.

    Returns:
        str: A string with only single spaces between terms.
    """
    return " ".join(str_var.split())


@validate_call
def insert_text_at_start_of_file(
    file_path: Path,
    text_to_insert: Annotated[str, StringConstraints(min_length=1)],
) -> None:
    """Insert the specified text at the start of the file.

    Args:
        file_path (Path): Full path to the target file.
        text_to_insert (str): Text to insert at the start of the file with a
        minimum length of 1 character.
    """
    with file_path.open(mode="r+", encoding="utf-8") as file:
        original_text = file.read()
        file.seek(0)
        file.write(f"{text_to_insert}{original_text}")


# TODO(xoren): Add unit tests
@wraps(rich.inspect)
def inspect(*args, **kwds) -> None:
    """Calls the inspect function of the Rich library to format and pretty
    prints object data.

    Args:
        target (object): A Python object instance.
    """

    rich.inspect(*args, **kwds)


# TODO(xoren): Add unit tests
@wraps(rich.print_json)
def print_json(*args, **kwds) -> None:
    """Calls the print JSON function of the Rich library to format and pretty
    prints data.

    Args:
        json_data (str): A JSON data string.
    """
    rich.print_json(*args, **kwds)


@validate_call
def read_file(file_path: Path) -> str:
    """Read the specified file.

    Args:
        file_path (Path): Full path for the file to be read.

    Returns:
        str: A string with the contents of the file.
    """
    file_contents: str

    with file_path.open(mode="r", encoding="utf-8") as file:
        file_contents = file.read()

    return file_contents


@validate_call
def rename_to_hidden_file(file_path: Path) -> Path:
    """Renames a file by adding a . (dot) to the start of the filename to
    make it hidden.

    Args:
        file_path (Path): Full path to the target file.

    Returns:
        Path: Full path to the renamed file.
    """

    file_dir: Path = file_path.parent
    filename: str = file_path.name

    # Add . to start of filename.
    new_file_path: Path = file_dir.joinpath(f".{filename}")
    return file_path.rename(new_file_path)


@validate_call
def run_ansible_command(
    host: Annotated[
        str, StringConstraints(min_length=3, pattern=ANSIBLE_HOST_PATTERN)
    ] = "localhost",
    module: Annotated[
        str, StringConstraints(min_length=3, pattern=ANSIBLE_MODULE_PATTERN)
    ] = "ansible.builtin.debug",
    module_args: str = str(uuid.uuid4),
    extra_vars: str = "",
) -> subprocess.CompletedProcess:
    """Run the Ansible command with the specified parameters.

    Args:
        host (str, optional): A host or group with a minimum length of 3
        characters. Defaults to "localhost".
        module (str, optional): An Ansible module with a minimum length of 3
        characters. Defaults to "ansible.builtin.debug".
        module_args (str, optional): Arguments for the module. Defaults to
        str(uuid.uuid4).
        extra_vars (str, optional): Additional variables file. Defaults to "".

    Returns:
        subprocess.CompletedProcess: An instance of CompletedProcess class.
    """
    script: str = f"ansible {host} -m {module}"

    if module_args:
        script += f" -a {module_args}"

    if extra_vars:
        script += f" -e '@{extra_vars}'"

    output: subprocess.CompletedProcess

    try:
        output = run_script(script=script)
    except RuntimeError as error:
        raise RuntimeError("Error running Ansible command.") from error

    print(output.stdout)
    return output


# TODO(xoren): Add unit tests
@validate_call
def run_ansible_playbook_command(
    playbook: Annotated[
        str,
        StringConstraints(min_length=3),
    ],
    options: str = "",
) -> Dict[str, Any]:
    """Run the Ansible playbook command with the specified parameters.

    Args:
        playbook (str): A valid Ansible playbook filename or path.
        options (str, optional): A space delimited string of playbook command
        options. Refer 'ansible-playbook --help' or Ansible's documentation
        (https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html) for
        all the options.

    Returns:
        Dict[str, Any]: A dictionary containing the process return values of
        return code, stdout, and stderr.
    """
    if not Path(playbook).exists():
        raise FileNotFoundError(
            f"Ansible playbook path '{playbook}' is not valid."
        )

    args: List[str] = ["ansible-playbook", playbook]

    if options:
        args.extend(options.split())

    return run_command(args=args)


# TODO(xoren): Add unit tests
def run_ansible_vault_view_command(encrypted_file_path: Path) -> Dict[str, Any]:
    """Runs the Ansible vault command to view encrypted files.

    Args:
        encrypted_file_path (Path): An Ansible vault encrypted file path.

    Returns:
        Dict[str, Any]: A dictionary containing the process return values of
        return code, stdout, and stderr.
    """
    args: List[str] = ["ansible-vault", "view", str(encrypted_file_path)]
    return run_command(args=args)


# TODO(xoren): Add unit tests
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
            ) from error
        except OSError as error:
            raise RuntimeError(
                f"OSError ({error}) running command {args}, output=[{output}]."
            ) from error
        except Exception as error:
            raise RuntimeError(
                f"Error ({error}) running command {args}, output=[{output}]."
            ) from error
        finally:
            stdout, stderr = process.communicate()
            return_code = process.returncode
            output = {
                "return_code": return_code,
                "stderr": stderr,
                "stdout": stdout,
            }

    return output


@validate_call
def run_script(
    script: Annotated[str, StringConstraints(min_length=2)],
) -> subprocess.CompletedProcess:
    """Run Bash scripts using Python.

    Args:
        script (str): A Bash script with a minimum length of 2 characters.

    Raises:
        RuntimeError: If the script causes any errors

    Returns:
        subprocess.CompletedProcess: An instance of CompletedProcess class.
    """
    output: subprocess.CompletedProcess

    try:
        output = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            check=True,
            text=True,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as error:
        print(f"\nSTDOUT: {error.stdout}\n")
        print(f"STDERR: {error.stderr}\n")
        print(f"RETURN_CODE: {error.returncode}\n")
        raise RuntimeError(error.stderr) from error

    return output


@validate_call
def set_file_to_readonly(file_path: Path) -> None:
    """Sets the specified file to readonly for the owner.

    Args:
        file_path (Path): Full path to the target file.
    """

    file_path.chmod(S_IREAD)


@validate_call
def validate_semantic_version_number(
    semantic_version: Annotated[str, StringConstraints(min_length=1)],
) -> bool:
    """Validates semantic version numbers.

    Args:
        semantic_version (str): A semantic version number with a minimum length
        of 1 character.

    Returns:
        bool: True if the semantic version number string in the correct format.
    """
    return isinstance(version.parse(semantic_version), version.Version)
