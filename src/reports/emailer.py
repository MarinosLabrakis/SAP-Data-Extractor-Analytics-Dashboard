"""SMTP delivery for executive reports."""
from __future__ import annotations
from email.message import EmailMessage
from pathlib import Path
import mimetypes
import smtplib

from ..core.config import get_settings
from ..core.logging import get_logger

log = get_logger(__name__)


def send_report(*, subject: str, attachments: list[Path], body: str = "See attached.") -> None:
    s = get_settings()
    if not s.smtp_host or not s.smtp_to:
        log.warning("SMTP not configured — skipping email delivery")
        return

    msg = EmailMessage()
    msg["From"] = s.smtp_user
    msg["To"] = s.smtp_to
    msg["Subject"] = subject
    msg.set_content(body)

    for path in attachments:
        ctype, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        msg.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)

    with smtplib.SMTP_SSL(s.smtp_host, s.smtp_port) as smtp:
        smtp.login(s.smtp_user, s.smtp_password)
        smtp.send_message(msg)
    log.info("Sent %s with %s attachment(s)", subject, len(attachments))
