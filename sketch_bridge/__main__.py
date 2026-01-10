"""Entry point for running SketchBridge as a module.

Usage:
    python -m sketch_bridge
"""

import sys

from .app import main

if __name__ == "__main__":
    sys.exit(main())
