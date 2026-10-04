"""Wikipedia lookup tool for Friday."""

from __future__ import annotations

import wikipedia


def lookup_wikipedia(topic: str) -> str:
    """Return a short summary for the requested topic."""
    try:
        return wikipedia.summary(topic, sentences=2)
    except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError, ValueError):
        fallback_topic = topic.replace(" ", "")
        return wikipedia.summary(fallback_topic, sentences=2)
