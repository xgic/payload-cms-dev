import json

# Load the JSON file (assuming it contains a list of objects)
obj = json.load(
    open("tests/resources/xg_ais_playbook_results.json", encoding="utf-8")
)

# Iterate through the objects and remove the one(s) you want
for i in enumerate(obj):
    if obj[i]["ename"] == "ansible_facts":
        obj.pop(i)
        # break  # Stop after removing the first occurrence

# Write the updated JSON to a new file
# with open(
#     "tests/resources/xg_ais_playbook_results.json", "w", encoding="utf-8"
# ) as output_file:
#     json.dump(
#         obj, output_file, sort_keys=True, indent=4, separators=(",", ": ")
#     )
print(json.dumps(obj, sort_keys=True, indent=4, separators=(",", ": ")))
