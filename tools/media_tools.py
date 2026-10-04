"""Media playback tooling for Friday."""

from __future__ import annotations

import json

from youtube_search import YoutubeSearch

from tools.browser import open_url


def play_youtube_video(query: str) -> str | None:
    """Open the first YouTube result for a search query."""
    results = YoutubeSearch(query, max_results=10).to_json()
    results_data = json.loads(results)
    videos = results_data.get("videos") or []
    if not videos:
        return None

    url = "https://www.youtube.com/" + videos[0]["url_suffix"]
    if not open_url(url):
        return None
    return url
