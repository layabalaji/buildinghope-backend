"""
Email notifications — sends a "new unread message" alert to your org's
inbox whenever someone submits the contact form, with a link to the admin
login page.

Uses Resend (resend.com) rather than Gmail SMTP.
"""

import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY")

FROM_EMAIL = os.environ.get("FROM_EMAIL", "onboarding@resend.dev")
ORG_NOTIFICATION_EMAIL = os.environ.get("ORG_NOTIFICATION_EMAIL")
ADMIN_LOGIN_URL = os.environ.get("ADMIN_LOGIN_URL", "http://localhost:5500/admin/")


def send_new_message_notification(message_id: int, subject: str, sender_name: str) -> None:
    """Fire-and-forget — a flaky email should never block a contact form
    submission from saving, so failures are logged, not raised.

    The subject line includes the message ID so each notification email
    is guaranteed unique — otherwise Gmail groups same-subject emails
    into one conversation thread, making it look like a reply chain.
    """
    if not resend.api_key or not ORG_NOTIFICATION_EMAIL:
        print("Email not configured (RESEND_API_KEY/ORG_NOTIFICATION_EMAIL missing) — skipping notification.")
        return

    email_subject = f"New message #{message_id} from {sender_name}: {subject}"

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": ORG_NOTIFICATION_EMAIL,
            "subject": email_subject,
            "text": (
                f"New unread message from {sender_name}\n"
                f"Subject: {subject}\n\n"
                f"View it in the admin dashboard: {ADMIN_LOGIN_URL}"
            ),
        })
    except Exception as e:
        print(f"Failed to send notification email: {e}")