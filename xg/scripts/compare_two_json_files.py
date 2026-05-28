# TODO(xoren): Convert to an xg.util function
# Reference: https://gitlab.xorengames.com/xg/xg-ais/-/work_items/54
# Import the modules
import difflib
import json

# Open the JSON files
file1 = open("file1.json", "r")
file2 = open("file2.json", "r")

# Load the JSON data as Python objects
data1 = json.load(file1)
data2 = json.load(file2)

# Close the files
file1.close()
file2.close()

# Compare the Python objects
if data1 == data2:
    print("The JSON files are equal.")
else:
    print("The JSON files are not equal.")

# Convert the Python objects to JSON strings
string1 = json.dumps(data1, indent=4, sort_keys=True)
string2 = json.dumps(data2, indent=4, sort_keys=True)

# Compare the JSON strings using difflib
diff = difflib.context_diff(string1.splitlines(), string2.splitlines())
delta = "\n".join(diff)
print(delta)
