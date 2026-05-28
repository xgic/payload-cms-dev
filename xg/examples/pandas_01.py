"""Our first pandas module."""

import json
from pathlib import Path

import pandas as pd

# json_file = Path(
#     "/home/xg-ais/source/xg-ais/tests/ansible/roles/docker_host/"
#     "docker_hosts_success_clean_install.json"
# )
json_file = Path("xg/examples/ansbile_playbook_plays.json")
assert json_file.exists()

# Load the JSON file as a dictionary
# with open(json_file, encoding="utf-8") as f:
#     data = json.load(f)

# Normalize the JSON data into a pandas DataFrame
# df = pd.json_normalize(
#     data,
#     record_path=["plays", "tasks"],
#     meta=["play", "task", ["hosts", "localhost", "stdout"]],
# )
# df = df[["play", "task", "host.localhost.stdout"]]
# df.columns = ["Play", "Task", "Output"]
# print(df)
# df = pd.json_normalize(
#     data,
#     # "plays",
#     # {"play", "tasks"},
# )
df = pd.read_json(json_file)

print(df)
