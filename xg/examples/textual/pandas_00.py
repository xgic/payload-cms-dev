"""Our first pandas module."""

import json

import pandas as pd

with open(
    (
        "/home/xg-ais/source/xg-ais/tests/ansible/roles/docker_host/"
        "docker_hosts_success_clean_install.json"
    ),
    encoding="utf-8",
) as f:
    results = json.load(f)

df = pd.json_normalize(results)
print(df)

# Current output:
#                                                plays  stats.test00.changed  stats.test00.failures  stats.test00.ignored  stats.test00.ok  stats.test00.rescued  stats.test00.skipped  stats.test00.unreachable
# 0  [{'play': {'duration': {'end': '2024-02-02T05:...                     2                      0                     1                9                     0                     0                         0
