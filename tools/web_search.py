"""Tool wrapper for searching the web with Google."""

from __future__ import annotations

from googlesearch import search


def search_google(query: str, num_results: int = 5) -> list[str]:
    """Query Google and return a list of result URLs."""
    links: list[str] = []
    for result in search(term=query, num_results=num_results, sleep_interval=2, timeout=10):
        url = str(result)
        if url:
            links.append(url)
    return links
