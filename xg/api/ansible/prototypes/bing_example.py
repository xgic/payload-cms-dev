# Import the Ansible API modules
# Source: https://www.bing.com/search?q=How+can+I+retrieve+the+value+of+an+Ansible+variable+from+an+external+Python+script+using+the+Ansible+Python+API+and+passing+Ansible+vault+authentication%3F&qs=n&form=QBRE&sp=-1&lq=1&pq=how+can+i+retrieve+the+value+of+an+ansible+variable+from+an+external+python+script+using+the+ansible+python+api+and+passing+ansible+vault+authentication%3F&sc=0-153&sk=&cvid=B545E38F3D4242AEBBB7139B91DD2F29&ghsh=0&ghacc=0&ghpl=
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import VaultLib, VaultSecret
from ansible.vars.manager import VariableManager

# Define the vault password and the variable name
vault_password = b"secret"
variable_name = "my_var"

# Create a VaultSecret object with the vault password
vault_secret = VaultSecret(vault_password)

# Create a VaultLib object with the VaultSecret object
vault = VaultLib([(vault_secret, vault_password)])

# Create a DataLoader object and set the vault object
loader = DataLoader()
loader.set_vault_secrets([("default", vault)])

# Create an InventoryManager object with the loader and the inventory file
inventory = InventoryManager(loader=loader, sources="hosts.yml")

# Create a VariableManager object with the loader and the inventory
variable_manager = VariableManager(loader=loader, inventory=inventory)

# Get the value of the variable from the inventory
variable_value = variable_manager.get_vars()["hostvars"]["localhost"][
    variable_name
]

# Print the value of the variable
print(variable_value)
