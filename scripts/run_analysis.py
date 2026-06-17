"""Reproducible analysis entry point.

This script currently prepares the project output directories only.
Full model estimation and reporting will be added in a later phase.
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.paths import (
    FIGURES_DIR,
    INTERMEDIATE_DIR,
    LOGS_DIR,
    MAIN_DATA_PATH,
    OUTPUT_DIR,
    TABLES_DIR,
)


def ensure_output_dirs() -> None:
    """Create output directories required by the reproducible pipeline."""
    for path in (OUTPUT_DIR, TABLES_DIR, FIGURES_DIR, LOGS_DIR, INTERMEDIATE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    ensure_output_dirs()

    print("Reproducible analysis scaffold")
    print(f"Input data: {MAIN_DATA_PATH}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Tables directory: {TABLES_DIR}")
    print(f"Figures directory: {FIGURES_DIR}")
    print(f"Logs directory: {LOGS_DIR}")
    print(f"Intermediate directory: {INTERMEDIATE_DIR}")

    # TODO: Load and validate the main monthly parcel dataset.
    # TODO: Create event dummy variables used by the state-space models.
    # TODO: Estimate baseline, simple-event, and proposed models.
    # TODO: Export model comparison and parameter tables.
    # TODO: Generate reproducible figures for paper_2.tex.
    # TODO: Save run metadata and diagnostics.


if __name__ == "__main__":
    main()
