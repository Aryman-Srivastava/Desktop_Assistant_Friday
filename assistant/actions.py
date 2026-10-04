"""Callable action handlers for the Friday assistant."""

from __future__ import annotations

import datetime
import json
import os
import smtplib
import sys
from typing import Any

import webbrowser
import wikipedia
from googlesearch import search
from youtube_search import YoutubeSearch

from config import (
    BROWSER_EXECUTABLE,
    PYCHARM_EXECUTABLE,
    require_email_credentials,
    resolve_contact_email,
)
from .guardrails import validate_intent, validate_url
from .models import ActionResult, AssistantCommand


def search_google(query: str, num_results: int = 5) -> list[str]:
    """Query Google and return the first few result URLs."""
    links: list[str] = []
    for result in search(term=query, num_results=num_results, sleep_interval=2, timeout=10):
        url = str(result)
        if url:
            links.append(url)
    return links


def open_url(url: str) -> bool:
    """Open a URL using the configured browser or default system browser."""
    if not validate_url(url):
        return False

    try:
        if BROWSER_EXECUTABLE:
            browser = webbrowser.BackgroundBrowser(BROWSER_EXECUTABLE)
            return bool(browser.open(url))
        return bool(webbrowser.open(url))
    except (OSError, webbrowser.Error):
        return bool(webbrowser.open(url))


def send_email_action(recipient_name: str, content: str) -> bool:
    """Send an email using Gmail app credentials."""
    sender, password = require_email_credentials()
    normalized_name = recipient_name.strip().lower()
    recipient = resolve_contact_email(normalized_name)

    if recipient is None and " " in normalized_name:
        recipient = resolve_contact_email(normalized_name.split()[-1])

    if recipient is None:
        return False

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, content)
    return True


def handle_wikipedia_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    topic = (command.parameters.get("topic") or "").strip()
    if not topic:
        return ActionResult(ok=False, message="What would you like me to look up?")

    try:
        result = wikipedia.summary(topic, sentences=2)
    except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError, ValueError):
        try:
            result = wikipedia.summary(topic.replace(" ", ""), sentences=2)
        except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError, ValueError):
            return ActionResult(ok=False, message="I could not find a matching Wikipedia page.")

    return ActionResult(ok=True, message=result)


def handle_play_media_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    query = (command.parameters.get("query") or "").strip()
    if not query:
        return ActionResult(ok=False, message="What would you like me to play?")

    results = YoutubeSearch(query, max_results=10).to_json()
    results_data = json.loads(results)
    videos = results_data.get("videos") or []
    if not videos:
        return ActionResult(ok=False, message="I could not find a matching YouTube result.")

    url = "https://www.youtube.com/" + videos[0]["url_suffix"]
    opened = open_url(url)
    if not opened:
        return ActionResult(ok=False, message="I could not open the YouTube link.")
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

    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    return ActionResult(ok=True, message=f"the time is {current_time}")


def handle_python_action(command: AssistantCommand) -> ActionResult:
    validation = validate_intent(command)
    if not validation.ok:
        return validation

    if PYCHARM_EXECUTABLE and os.path.exists(PYCHARM_EXECUTABLE):
        os.startfile(PYCHARM_EXECUTABLE)
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

    for root, _, files in os.walk("C:"):
        if query.lower() in [item.lower() for item in files]:
            os.startfile(os.path.join(root, query))
            return ActionResult(ok=True, message="Opening file.", data={"file": os.path.join(root, query)})

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
