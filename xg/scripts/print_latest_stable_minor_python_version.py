"""
Prints the latest stable major and minor Python version numbers from GitHub in
the 0.00 format.
"""

import sys

from packaging import version

from xg.util import get_latest_stable_python_version


def main() -> None:
    """Main function."""
    latest_version: version.Version
    verbose: bool = False

    if len(sys.argv) == 2 and sys.argv[1].lower() == "-v":
        verbose = True

    latest_version = get_latest_stable_python_version(verbose=verbose)
    print(f"{latest_version.major}.{latest_version.minor}")


main()
