"""Command registry used by the Friday assistant."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .intent_parser import IntentResult


class CommandRouter:
    """Simple registry that maps an intent name to a handler."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[dict[str, str], dict[str, Any]], Any]] = {}

    def register(self, intent_name: str, handler: Callable[[dict[str, str], dict[str, Any]], Any]) -> None:
        self._handlers[intent_name] = handler

    def dispatch(self, intent: IntentResult, context: dict[str, Any] | None = None) -> Any:
        handler = self._handlers.get(intent.intent)
        if handler is None:
            raise KeyError(f"No registered handler for intent '{intent.intent}'")
        return handler(intent.parameters, context or {})

    def has_handler(self, intent_name: str) -> bool:
        return intent_name in self._handlers
