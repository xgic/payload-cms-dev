# Import the Ansible API module
from ansible.module_utils.basic import AnsibleModule


# Define the ping function
def ping(hosts):
    # Create an Ansible module instance
    module = AnsibleModule(
        argument_spec=dict(
            hosts=dict(type="list", required=True)  # The list of hosts to ping
        )
    )
    # Get the hosts parameter from the module
    hosts = module.params["hosts"]
    # Initialize an empty result dictionary
    result = dict(changed=False, pinged=[])
    # Loop through the hosts
    for host in hosts:
        # Try to ping the host using the ping module
        rc, out, err = module.run_command("ansible %s -m ping" % host)
        # If the ping was successful, append the host to the pinged list
        if rc == 0:
            result["pinged"].append(host)
        # Otherwise, fail the module with the error message
        else:
            module.fail_json(msg=err)
    # Return the result dictionary
    module.exit_json(**result)


# Call the ping function with the hosts argument
ping(hosts=["localhost"])
