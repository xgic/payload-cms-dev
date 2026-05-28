"""Prints the latest stable Python semantic version number from GitHub."""

import sys

from xg.util import get_latest_stable_python_version


def main() -> None:
    """Main function."""
    verbose: bool = False

    if len(sys.argv) == 2 and sys.argv[1].lower() == "-v":
        verbose = True

    print(get_latest_stable_python_version(verbose=verbose))


main()
