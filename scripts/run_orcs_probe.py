"""Run the ORCS metadata pilot directly from a source checkout.

This launcher adds the repository's ``src`` directory to Python's import path so
the pilot can run before the package is installed. It contains no credentials;
the key location remains an explicit command-line input.
"""

from __future__ import annotations

import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from deathmap_ai.cli import main  # noqa: E402 - source path is configured above.


if __name__ == "__main__":
    main()
