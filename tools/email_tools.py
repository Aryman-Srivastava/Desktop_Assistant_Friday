"""Email tool for Friday."""

from __future__ import annotations

import smtplib

from config import require_email_credentials, resolve_contact_email


def send_email_action(recipient_name: str, content: str) -> bool:
    """Send email using the configured Gmail App Password."""
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
