# Import the required modules
from pathlib import Path

from ansible.cli.playbook import PlaybookCLI
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import PromptVaultSecret, VaultLib, VaultSecret
from ansible.vars.manager import VariableManager

# from ansible.parsing.vault import VaultLib, b_HEADER, is_encrypted, is_encrypted_file, parse_vaulttext_envelope, PromptVaultSecret
HOME_DIR = Path.home()
APP_DIR = Path.cwd()
ANSIBLE_DIR = APP_DIR.joinpath("ansible")
TESTS_DIR = APP_DIR.joinpath("tests")
if (
    not HOME_DIR.exists()
    or not APP_DIR.exists()
    or not ANSIBLE_DIR.exists()
    or not TESTS_DIR.exists()
):
    error = FileNotFoundError(
        "Directory not found error checking XG AIS application paths."
    )
    error.args += (f"HOME_DIR[{HOME_DIR}] exists = {HOME_DIR.exists()}",)
    error.args += (f"HOME_DIR[{APP_DIR}] exists = {APP_DIR.exists()}",)
    error.args += (f"HOME_DIR[{ANSIBLE_DIR}] exists = {ANSIBLE_DIR.exists()}",)
    error.args += (f"HOME_DIR[{TESTS_DIR}] exists = {TESTS_DIR.exists()}",)
    raise error


class XGAnsiblePlaybook(PlaybookCLI):
    # create base objects
    def __init__(self):
        super().__init__(self)
        pass

    def run(self):
        # super().run()
        # super().__init__(args=args,)
        loader, inventory, variable_manager = self._play_prereqs()
        # Get the variables for a host or group
        variables = variable_manager.get_vars(
            host=inventory.get_host("localhost")
        )
        print(variables)


playbook = XGAnsiblePlaybook()
playbook.run()
