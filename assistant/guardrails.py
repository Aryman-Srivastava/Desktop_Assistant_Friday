"""General guardrails and validation helpers for Friday actions."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from config import FRIDAY_MAX_COMMAND_LENGTH, FRIDAY_MAX_MESSAGE_LENGTH
from .models import ActionResult, AssistantCommand

MAX_COMMAND_LENGTH = FRIDAY_MAX_COMMAND_LENGTH
MAX_MESSAGE_LENGTH = FRIDAY_MAX_MESSAGE_LENGTH
MAX_TOPIC_LENGTH = 200
ALLOWED_INTENTS = {
    "wikipedia",
    "play_media",
    "search_web",
    "time",
    "open_python",
    "send_email",
    "find_file",
    "exit",
    "unknown",
}


def sanitize_user_input(value: str, *, max_length: int = MAX_COMMAND_LENGTH) -> str:
    """Remove control characters and limit free-form input length."""
    clean_value = re.sub(r"[\x00-\x1f\x7f]+", " ", value or "")
    clean_value = " ".join(clean_value.split())
    if len(clean_value) > max_length:
        return clean_value[:max_length].rstrip()
    return clean_value


def validate_intent(command: AssistantCommand) -> ActionResult:
    """Reject unsupported or unsafe command payloads early."""
    if command.intent not in ALLOWED_INTENTS:
        return ActionResult(
            ok=False,
            message="Unsupported command type.",
            error=f"Unsupported intent: {command.intent}",
        )

    if not sanitize_user_input(command.raw_query or ""):
        return ActionResult(ok=False, message="I did not catch that command.", error="Empty query")

    if len(command.raw_query) > MAX_COMMAND_LENGTH:
        return ActionResult(
            ok=False,
            message="That command is too long for safe processing.",
            error="Command exceeds configured limit",
        )

    if command.intent == "send_email":
        recipient = (command.parameters.get("recipient") or "").strip()
        message = (command.parameters.get("message") or "").strip()
        if not recipient:
            return ActionResult(ok=False, message="I need a valid recipient name.", error="Missing recipient")
        if len(message) > MAX_MESSAGE_LENGTH:
            return ActionResult(
                ok=False,
                message="The email body is too long.",
                error="Email content exceeds safe limit",
            )

    if command.intent in {"wikipedia", "search_web", "play_media", "find_file"}:
        query = (command.parameters.get("query") or command.parameters.get("topic") or "").strip()
        if len(query) > MAX_TOPIC_LENGTH:
            return ActionResult(
                ok=False,
                message="The search term is too long for safe processing.",
                error="Search query exceeds safe limit",
            )

    return ActionResult(ok=True, message="Command validated.")


def validate_url(url: str) -> bool:
    """Ensure the target is a sane URL before opening it."""
    parsed = urlparse(url)
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc)
