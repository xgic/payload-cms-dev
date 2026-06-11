#!/usr/bin/env python3
"""Return the name of the generated Payload project folder.

Reads from .devcontainer/create-payload-config.json if present.
Always produces a safe default so tools/scripts have a reliable
project name.
"""

import json
import os
import sys

CONFIG = ".devcontainer/create-payload-config.json"
DEFAULT = "my-payload-cms"

if not os.path.exists(CONFIG):
    print(DEFAULT)
    sys.exit(0)

try:
    with open(CONFIG, encoding="utf-8") as f:
        data = json.load(f)
    name = data.get("projectName") or DEFAULT
    print(name)
except Exception:
    # Never let a bad config or json error break tools or scripts
    print(DEFAULT)
