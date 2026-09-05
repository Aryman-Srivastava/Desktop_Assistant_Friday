"""Application configuration loaded from environment variables."""

import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

PROJECT_ROOT = Path(__file__).resolve().parent
if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")

CONTACTS_FILE = PROJECT_ROOT / os.getenv("FRIDAY_CONTACTS_FILE", "contacts.json")
BROWSER_EXECUTABLE = os.getenv("FRIDAY_BROWSER_EXECUTABLE", "")
PYCHARM_EXECUTABLE = os.getenv("FRIDAY_PYCHARM_EXECUTABLE", "")
GMAIL_ADDRESS = os.getenv("FRIDAY_GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("FRIDAY_GMAIL_APP_PASSWORD", "")


def load_contacts() -> dict[str, str]:
    """Load named email contacts from the configured JSON file."""
    with CONTACTS_FILE.open(encoding="utf-8") as contacts_file:
        contacts = json.load(contacts_file)

    if not isinstance(contacts, dict) or not all(
        isinstance(name, str) and isinstance(address, str)
        for name, address in contacts.items()
    ):
        raise ValueError("contacts.json must contain a name-to-email mapping")
    return {name.lower(): address for name, address in contacts.items()}


def require_email_credentials() -> tuple[str, str]:
    """Return Gmail credentials or fail with an actionable configuration error."""
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        raise RuntimeError(
            "Set FRIDAY_GMAIL_ADDRESS and FRIDAY_GMAIL_APP_PASSWORD in .env"
        )
    return GMAIL_ADDRESS, GMAIL_APP_PASSWORD
