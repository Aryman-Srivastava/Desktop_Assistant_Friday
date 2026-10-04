"""Pydantic models for Friday assistant inputs and outputs."""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def clean_text(value: str, max_length: int = 500) -> str:
    """Normalize and clamp free-form assistant text."""
    clean_value = re.sub(r"[\x00-\x1f\x7f]+", " ", value or "")
    clean_value = " ".join(clean_value.split())
    if len(clean_value) > max_length:
        return clean_value[:max_length].rstrip()
    return clean_value


class AssistantCommand(BaseModel):
    """Structured representation of a parsed user command."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    intent: Literal[
        "wikipedia",
        "play_media",
        "search_web",
        "time",
        "open_python",
        "send_email",
        "find_file",
        "exit",
        "unknown",
    ] = "unknown"
    parameters: dict[str, str] = Field(default_factory=dict)
    requires_confirmation: bool = False
    raw_query: str = ""

    @field_validator("raw_query")
    @classmethod
    def validate_raw_query(cls, value: str) -> str:
        return clean_text(value, max_length=240)

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, value: dict[str, str]) -> dict[str, str]:
        cleaned: dict[str, str] = {}
        for key, item in value.items():
            cleaned[key] = clean_text(str(item), max_length=500)
        return cleaned

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class ActionResult(BaseModel):
    """Standard response object for assistant actions."""

    model_config = ConfigDict(extra="forbid")

    ok: bool = False
    message: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None

    @field_validator("message", "error")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return clean_text(value, max_length=500)
