"""Entry point for running the invoicer package as a module."""

import sys

from invoicer.cli import main

# Run the main function and exit with its return code
if __name__ == "__main__":
    sys.exit(main())
