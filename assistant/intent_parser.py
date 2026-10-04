"""Lightweight intent parsing for Friday voice commands."""

from __future__ import annotations

import re

from .models import AssistantCommand


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split()).strip()


def _extract_contact_name(query: str, known_contacts: dict[str, str] | None) -> str | None:
    if not known_contacts:
        return None

    normalized = _normalize_text(query)
    for name in sorted(known_contacts, key=len, reverse=True):
        pattern = rf"(?<![a-z]){re.escape(name)}(?![a-z])"
        if re.search(pattern, normalized):
            return name
    return None


def _extract_email_message(query: str) -> str:
    cleaned = _normalize_text(query)
    for prefix in ("email ", "send email ", "mail "):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break

    for marker in (" to ", " for ", " to whom ", " to who ", " recipient "):
        if marker in cleaned:
            cleaned = cleaned.split(marker, 1)[1]
            break

    return cleaned.strip()


def parse_user_intent(query: str, known_contacts: dict[str, str] | None = None) -> AssistantCommand:
    """Map a spoken command to a structured intent."""
    normalized = _normalize_text(query)
    if not normalized:
        return AssistantCommand(intent="unknown", parameters={}, requires_confirmation=False, raw_query=query)

    if any(phrase in normalized for phrase in ("exit", "bye", "goodbye", "shutdown")):
        return AssistantCommand(intent="exit", parameters={}, requires_confirmation=False, raw_query=query)

    if "time" in normalized:
        return AssistantCommand(intent="time", parameters={}, requires_confirmation=False, raw_query=query)

    if "wikipedia" in normalized:
        topic = normalized.replace("wikipedia", "").strip()
        return AssistantCommand(
            intent="wikipedia",
            parameters={"topic": topic or "general"},
            requires_confirmation=False,
            raw_query=query,
        )

    if "youtube" in normalized or "play" in normalized:
        topic = normalized.replace("youtube", "").replace("play", "").strip()
        return AssistantCommand(
            intent="play_media",
            parameters={"query": topic or "music"},
            requires_confirmation=False,
            raw_query=query,
        )

    if "search" in normalized or "google" in normalized:
        search_term = normalized.replace("search", "").replace("google", "").strip()
        return AssistantCommand(
            intent="search_web",
            parameters={"query": search_term or "latest news"},
            requires_confirmation=False,
            raw_query=query,
        )

    if "python" in normalized or "pycharm" in normalized:
        return AssistantCommand(intent="open_python", parameters={}, requires_confirmation=False, raw_query=query)

    if "email" in normalized or "mail" in normalized:
        recipient = _extract_contact_name(normalized, known_contacts) or ""
        message = _extract_email_message(normalized)
        return AssistantCommand(
            intent="send_email",
            parameters={"recipient": recipient, "message": message},
            requires_confirmation=True,
            raw_query=query,
        )

    if "find file" in normalized or "open file" in normalized or "os" in normalized:
        query_param = (
            normalized.replace("find file", "")
            .replace("open file", "")
            .replace("os", "")
            .strip()
        )
        return AssistantCommand(
            intent="find_file",
            parameters={"query": query_param},
            requires_confirmation=False,
            raw_query=query,
        )

    return AssistantCommand(intent="unknown", parameters={"query": normalized}, requires_confirmation=False, raw_query=query)


IntentResult = AssistantCommand
