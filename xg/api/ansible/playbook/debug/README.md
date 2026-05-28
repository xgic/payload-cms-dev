# XG Ansible Playbook Debugger Textual App

## Accelerating Ansible development through intelligent testing and debugging.

The Xoren Games Ansible Playbook Debugger Textual app aims to accelerate Ansible development and testing.

## Running Tests
There are currently three ways to debug playbooks using this Textual app:
- VS Code Debugging (F5 key)
- Python Module
- Textual Console

### VS Code Debugging
Open a playbook YAML file in VS Code and press the F5 key to launch the debugger
app.

### Python Module
```
# Debug default Ansible playbook.
python -m xg.api.ansible.playbook.debug

# Debug main Ansible playbook.
python -m xg.api.ansible.playbook.debug -f ansible/xg_ais.yml
```

# Textual Console Debugging
```
# Start Textual Console to view detailed information for debugging.
textual console

# Debug with Textual
textual run --dev  xg.api.ansible.playbook.debug
```