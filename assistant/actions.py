"""Callable action handlers for the Friday assistant."""

from __future__ import annotations

import datetime
import os
import sys
from typing import Any

from config import PYCHARM_EXECUTABLE
from tools.browser import open_url
from tools.email_tools import send_email_action
from tools.media_tools import play_youtube_video
from tools.system_tools import find_file, open_python_app, tell_time
from tools.web_search import search_google
from tools.wikipedia_tool import lookup_wikipedia
from .guardrails import validate_intent
from .models import ActionResult, AssistantCommand


def handle_wikipedia_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    topic = (command.parameters.get("topic") or "").strip()
    if not topic:
        return ActionResult(ok=False, message="What would you like me to look up?")

    try:
        result = lookup_wikipedia(topic)
    except Exception:
        return ActionResult(ok=False, message="I could not find a matching Wikipedia page.")

    return ActionResult(ok=True, message=result)


def handle_play_media_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    query = (command.parameters.get("query") or "").strip()
    if not query:
        return ActionResult(ok=False, message="What would you like me to play?")

    url = play_youtube_video(query)
    if not url:
        return ActionResult(ok=False, message="I could not find a matching YouTube result.")
    return ActionResult(ok=True, message="Opening YouTube.", data={"url": url})


def handle_search_web_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    query = (command.parameters.get("query") or "").strip()
    if not query:
        return ActionResult(ok=False, message="What would you like me to search for?")

    links = search_google(query)
    if not links:
        return ActionResult(ok=False, message="No search results were found.")

    opened = open_url(str(links[0]))
    if not opened:
        return ActionResult(ok=False, message="I could not open the search result.")
    return ActionResult(ok=True, message="Opening the top result.", data={"url": str(links[0])})


def handle_time_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    current_time = tell_time()
    return ActionResult(ok=True, message=f"the time is {current_time}")


def handle_python_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    if open_python_app():
        return ActionResult(ok=True, message="Opening PyCharm.")
    return ActionResult(ok=False, message="PyCharm path is not configured.")


def handle_send_email_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    recipient = (command.parameters.get("recipient") or "").strip()
    message = (command.parameters.get("message") or "").strip()
    if not recipient or not message:
        return ActionResult(ok=False, message="I need both a recipient and message content.")

    sent = send_email_action(recipient, message)
    if not sent:
        return ActionResult(ok=False, message="I could not send the email.")
    return ActionResult(ok=True, message="Email sent.")


def handle_find_file_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    query = (command.parameters.get("query") or "").strip()
    if not query:
        return ActionResult(ok=False, message="What file should I look for?")

    match = find_file(query)
    if match:
        os.startfile(match)
        return ActionResult(ok=True, message="Opening file.", data={"file": match})

    return ActionResult(ok=False, message="File not found.")


def handle_exit_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    raise SystemExit(0)


ACTION_MAP = {
    "wikipedia": handle_wikipedia_action,
    "play_media": handle_play_media_action,
    "search_web": handle_search_web_action,
    "time": handle_time_action,
    "open_python": handle_python_action,
    "send_email": handle_send_email_action,
    "find_file": handle_find_file_action,
    "exit": handle_exit_action,
}


def run_action(command: AssistantCommand) -> ActionResult:
    """Execute a validated assistant command."""
    if command.intent == "unknown":
        return ActionResult(ok=False, message="I could not understand that command.")

    handler = ACTION_MAP.get(command.intent)
    if handler is None:
        return ActionResult(ok=False, message="I do not support that action yet.")

    return handler(command)
