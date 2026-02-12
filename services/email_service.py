"""
Simple email service for sending capsule notifications.

This uses SMTP configuration from environment variables and is designed
to fail gracefully if email is not configured, so the core capsule
functionality still works without emails.
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime


logger = logging.getLogger(__name__)


class EmailService:
    """Service responsible for sending email notifications."""

    def __init__(self):
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("EMAIL_FROM")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "Time Capsule Cloud")
        self.use_ssl = os.getenv("SMTP_USE_SSL", "0") == "1" or self.port == 465
        # If host or from_email is missing, treat email as disabled
        self.enabled = bool(self.host and self.from_email)

        if not self.enabled:
            logger.warning("EmailService disabled: SMTP_HOST or EMAIL_FROM not set")
        else:
            logger.info(
                "EmailService enabled. Host=%s, Port=%s, Use SSL=%s, Username set=%s",
                self.host,
                self.port,
                self.use_ssl,
                bool(self.username),
            )

    def _send(self, to_email: str, subject: str, body: str):
        """Internal helper to send a plain text email."""
        if not self.enabled:
            # Do not raise; just log and skip
            logger.warning(
                "Skipping email to %s because EmailService is not configured "
                "(missing SMTP_HOST or EMAIL_FROM)",
                to_email,
            )
            return

        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = formataddr((self.from_name, self.from_email))
            msg["To"] = to_email

            # Choose SSL or STARTTLS based on configuration
            if self.use_ssl:
                smtp_class = smtplib.SMTP_SSL
            else:
                smtp_class = smtplib.SMTP

            with smtp_class(self.host, self.port) as server:
                server.ehlo()
                # Use STARTTLS only in non-SSL mode when username/password provided
                if not self.use_ssl and self.username and self.password:
                    try:
                        server.starttls()
                        server.ehlo()
                    except smtplib.SMTPException:
                        logger.warning("SMTP server does not support STARTTLS; continuing without it")
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)

            logger.info("Sent email to %s with subject '%s'", to_email, subject)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Failed to send email to %s: %s", to_email, exc)
            # Re-raise so that debug/test endpoints can surface the error
            raise

    # Public helpers for specific notification types

    def send_capsule_created_notification(
        self,
        recipient_email: str,
        recipient_name: str | None,
        sender_name: str | None,
        unlock_date: datetime,
    ):
        """
        Notify an existing user that a capsule has been created for them.
        The actual contents remain hidden.
        """
        display_recipient = recipient_name or "there"
        display_sender = sender_name or "someone"
        subject = "A time capsule has been created for you"
        body = (
            f"Hi {display_recipient},\n\n"
            f"{display_sender} has created a secret time capsule for you.\n"
            f"It is scheduled to unlock on {unlock_date.strftime('%Y-%m-%d %H:%M UTC')}.\n\n"
            "You will receive another email when the capsule unlocks.\n\n"
            "Best regards,\n"
            "Time Capsule Cloud"
        )
        self._send(recipient_email, subject, body)

    def send_capsule_created_external_notification(
        self,
        recipient_email: str,
        sender_name: str | None,
        unlock_date: datetime,
    ):
        """
        Notify a non-registered recipient (email only) that a capsule exists for them.

        The email explains that they must create an account with this email
        address to view the capsule once it unlocks.
        """
        display_sender = sender_name or "someone"
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        subject = "A time capsule has been created for you"
        body = (
            "Hi there,\n\n"
            f"{display_sender} has created a secret time capsule for you using this email address.\n"
            f"It is scheduled to unlock on {unlock_date.strftime('%Y-%m-%d %H:%M UTC')}.\n\n"
            "To view this capsule when it unlocks, please create an account on Time Capsule Cloud "
            "using this same email address:\n"
            f"{frontend_url}\n\n"
            "After you sign up and sign in, the capsule will appear in your dashboard when it unlocks.\n\n"
            "You will also receive another email on the day the capsule unlocks.\n\n"
            "Best regards,\n"
            "Time Capsule Cloud"
        )
        self._send(recipient_email, subject, body)

    def send_capsule_unlocked_notification(
        self,
        recipient_email: str,
        recipient_name: str | None,
        sender_name: str | None,
        unlock_date: datetime | None,
    ):
        """
        Notify recipient that their capsule is now unlocked.
        """
        display_recipient = recipient_name or "there"
        display_sender = sender_name or "someone"
        subject = "Your time capsule has unlocked"
        date_text = (
            unlock_date.strftime("%Y-%m-%d %H:%M UTC") if unlock_date else "now"
        )
        body = (
            f"Hi {display_recipient},\n\n"
            f"The time capsule from {display_sender} has just unlocked ({date_text}).\n"
            "Log in to Time Capsule Cloud to view your secret message or file.\n\n"
            "Best regards,\n"
            "Time Capsule Cloud"
        )
        self._send(recipient_email, subject, body)

    def send_capsule_date_updated_notification(
        self,
        recipient_email: str,
        recipient_name: str | None,
        sender_name: str | None,
        old_unlock_date: datetime,
        new_unlock_date: datetime,
    ):
        """
        Notify recipient that their capsule unlock date has been updated.
        """
        display_recipient = recipient_name or "there"
        display_sender = sender_name or "the sender"
        
        # Format dates nicely
        old_date_str = old_unlock_date.strftime('%Y-%m-%d at %H:%M UTC')
        new_date_str = new_unlock_date.strftime('%Y-%m-%d at %H:%M UTC')
        
        subject = "Your time capsule unlock date has been updated"
        body = (
            f"Hi {display_recipient}\n\n"
            f"The unlock date for your time capsule from {display_sender} has been updated.\n\n"
            f"Old unlock date: {old_date_str}\n"
            f"New unlock date: {new_date_str}\n\n"
            "The capsule will now unlock on the new date.\n\n"
            "Best regards,\n"
            "Time Capsule Cloud"
        )
        self._send(recipient_email, subject, body)

    def send_password_reset_email(
        self,
        recipient_email: str,
        recipient_name: str | None,
        reset_token: str,
    ):
        """
        Send password reset email with reset link.
        """
        display_recipient = recipient_name or "there"
        # In a real app, you'd construct a frontend URL with the token
        # For now, we'll include instructions
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        subject = "Password Reset Request"
        body = (
            f"Hi {display_recipient},\n\n"
            "You requested to reset your password for Time Capsule Cloud.\n\n"
            f"Click the link below to reset your password:\n{reset_url}\n\n"
            "This link will expire in 1 hour.\n\n"
            "If you didn't request this, please ignore this email.\n\n"
            "Best regards,\n"
            "Time Capsule Cloud"
        )
        self._send(recipient_email, subject, body)