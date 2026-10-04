"""Registry of Friday tools for dispatching actions."""

from __future__ import annotations

from .base import ToolSpec
from .browser import open_url
from .email_tools import send_email_action
from .media_tools import play_youtube_video
from .system_tools import find_file, open_python_app, tell_time
from .web_search import search_google
from .wikipedia_tool import lookup_wikipedia

TOOL_REGISTRY: dict[str, ToolSpec] = {
    "web_search": ToolSpec(
        name="web_search",
        description="Search the web and return leading results for a query.",
        func=search_google,
    ),
    "open_url": ToolSpec(
        name="open_url",
        description="Open a URL in the configured browser.",
        func=open_url,
    ),
    "wikipedia": ToolSpec(
        name="wikipedia",
        description="Look up a short summary from Wikipedia.",
        func=lookup_wikipedia,
    ),
    "play_media": ToolSpec(
        name="play_media",
        description="Play a YouTube video or music result for a query.",
        func=play_youtube_video,
    ),
    "time": ToolSpec(
        name="time",
        description="Return the current system time.",
        func=tell_time,
    ),
    "open_python": ToolSpec(
        name="open_python",
        description="Open PyCharm if configured on the machine.",
        func=open_python_app,
    ),
    "find_file": ToolSpec(
        name="find_file",
        description="Find a file by name on the local system.",
        func=find_file,
    ),
    "send_email": ToolSpec(
        name="send_email",
        description="Send an email to a known contact.",
        func=send_email_action,
    ),
}
