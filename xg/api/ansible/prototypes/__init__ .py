# Import the required modules
from pathlib import Path

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


# Define the vault password and the variable name
VAULT_ID = "xg_ais_vault_id"
# VAULT_ID = "xg_ais_vault_id".encode("utf-8")
# VAULT_PASSWORD = "TimXgais88"
VAULT_PASSWORD = "TimXgais88\r".encode("utf-8")
# variable_name = "my_var"

# Create a VaultSecret object with the vault password
vault_secret = VaultSecret(VAULT_PASSWORD)

# Create a VaultLib object with the VaultSecret object
vault = VaultLib([(vault_secret, VAULT_PASSWORD)])

# Create a DataLoader object
loader = DataLoader()
loader.set_basedir(str(ANSIBLE_DIR))
# loader.set_vault_secrets([("default", vault)])
# loader.set_vault_secrets(
#     [
#         (
#             VAULT_ID,
#             PromptVaultSecret("@/usr/local/bin/xg-ais-keyring-client"),
#         )
#     ]
# )

loader.set_vault_secrets(
    [
        (
            VAULT_ID,
            PromptVaultSecret(VAULT_PASSWORD),
        )
    ]
)

# loader.set_vault_secrets(
#     [
#         (
#             VAULT_ID,
#             PromptVaultSecret(None),
#         )
#     ]
# )

# Create an InventoryManager object
inventory_path = ANSIBLE_DIR.joinpath("inventories/development/hosts.yml")
if not inventory_path.exists():
    raise FileNotFoundError(f"Inventory file '{inventory_path}' not found.")


inventory = InventoryManager(loader=loader, sources=str(inventory_path))

# Create a VariableManager object
variable_manager = VariableManager(loader=loader, inventory=inventory)

# Get the variables for a host or group
variables = variable_manager.get_vars(host=inventory.get_host("localhost"))

# Print the value of a variable
print(variables["ansible_user"])
