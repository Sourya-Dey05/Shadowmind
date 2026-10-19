# =============================================================================
# FILE: src/utils/path_helper.py
# PURPOSE: Robust path resolution helper for PyInstaller bundles and local dev.
#          When packaged as a standalone .exe, PyInstaller extracts files to
#          `sys._MEIPASS`. This helper ensures config and model paths resolve correctly.
# =============================================================================

import sys
from pathlib import Path

def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).resolve().parents[2]

    return base_path / relative_path
