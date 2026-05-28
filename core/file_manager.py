"""Low-level, side-effect-free file helpers.

All functions return a success bool so callers can decide how to surface errors.
"""

import os
from pathlib import Path


def read_file(path: str) -> str | None:
    """Return file content as a string, or None on any error."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except Exception:
        return None


def write_file(path: str, content: str) -> bool:
    """Write *content* to *path*, creating parent directories as needed."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return True
    except Exception:
        return False


def delete_file(path: str) -> bool:
    """Delete *path*. Returns False if the file does not exist or on error."""
    try:
        os.remove(path)
        return True
    except Exception:
        return False


def file_exists(path: str) -> bool:
    return os.path.isfile(path)
