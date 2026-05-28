"""XG Ansible Playbook Debugger Textual App Constants Module"""

from typing import ClassVar

from pydantic import BaseModel


class XGAppConstants(BaseModel):
    """XG application constants.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from the Pydantic base model
        class.
    """

    APP_NAME: ClassVar[str] = "XG Ansible Playbook Debugger"
    APP_DESCRIPTION: ClassVar[str] = (
        "Runs an Ansible playbook and automatically parses its JSON output "
        "displaying a summary of the results and highlighting warnings and "
        "errors."
    )
    APP_DOCS_URL: ClassVar[str] = (
        "https://xgcms.xorengames.com/kb/xg/apps/xg-playbook-debugger"
    )
    APP_EPILOG: ClassVar[str] = f"For more information see '{APP_DOCS_URL}'."
    ARGS_INPUT: ClassVar[str] = (
        "An input file containing Ansible playbook results in JSON format. The "
        "input results file will be processed and analyzed, instead of running "
        "a playbook, to processes its output."
    )
    ARGS_JSON: ClassVar[str] = (
        "Print Ansible playbook results in JSON format to STDOUT in headless "
        "application mode (no Textual UI)."
    )
    ARGS_PLAYBOOK: ClassVar[str] = (
        "A relative or absolute Ansible playbook path."
    )
    ARGS_TIMEOUT: ClassVar[str] = (
        "A playbook timeout duration in seconds. The default is 180 seconds."
    )
    ARGS_VERBOSE: ClassVar[str] = "Print verbose playbook output."
    ERROR_CREATING_PYDANTIC_MODEL: ClassVar[str] = (
        "Error creating playbook results Pydantic model."
    )
    ERROR_LOADING_JSON_RESULTS: ClassVar[str] = "Error loading JSON results."
    ERROR_INPUT_FILE_NOT_FOUND: ClassVar[str] = (
        "Invalid Ansible playbook results input file path."
    )
    ERROR_INPUT_FILE_READ_ERROR: ClassVar[str] = (
        "An error occurred reading the specified Ansible playbook results "
        "input file."
    )
    ERROR_PLAYBOOK_FILE_NOT_FOUND: ClassVar[str] = (
        "Invalid Ansible playbook file path."
    )
