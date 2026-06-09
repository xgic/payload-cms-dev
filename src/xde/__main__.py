"""Allow running the package directly with python -m xde."""

from __future__ import annotations

import sys

from xde.cli import main

if __name__ == "__main__":
    sys.exit(main())
