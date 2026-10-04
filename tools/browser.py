"""Web browser helpers for Friday."""

from __future__ import annotations

import webbrowser

from config import BROWSER_EXECUTABLE
from assistant.guardrails import validate_url


def open_url(url: str) -> bool:
    """Open a URL using the configured browser or the default one."""
    if not validate_url(url):
        return False

    try:
        if BROWSER_EXECUTABLE:
            browser = webbrowser.BackgroundBrowser(BROWSER_EXECUTABLE)
            return bool(browser.open(url))
        return bool(webbrowser.open(url))
    except (OSError, webbrowser.Error):
        return bool(webbrowser.open(url))
