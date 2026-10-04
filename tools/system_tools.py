"""System tools for Friday: time, Python, file lookup."""

from __future__ import annotations

import datetime
import os

from config import PYCHARM_EXECUTABLE


def tell_time() -> str:
    """Return the current time as a string."""
    return datetime.datetime.now().strftime("%H:%M:%S")


def open_python_app() -> bool:
    """Open PyCharm when a configured path exists."""
    if PYCHARM_EXECUTABLE and os.path.exists(PYCHARM_EXECUTABLE):
        os.startfile(PYCHARM_EXECUTABLE)
        return True
    return False


def find_file(filename: str) -> str | None:
    """Return the first matching file path under the local C: drive."""
    normalized = filename.strip()
    if not normalized:
        return None

    for root, _, files in os.walk("C:"):
        if normalized.lower() in [item.lower() for item in files]:
            return os.path.join(root, normalized)
    return None
