import asyncio
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings

SMTP_TIMEOUT_SECONDS = 30


class EmailService:
    async def send_employee_created_email(
        self, to_email: str, employee_name: str
    ) -> None:
        """Send a simple welcome email without blocking the async event loop."""
        await asyncio.to_thread(
            self._send_employee_created_email_sync,
            to_email,
            employee_name,
        )

    @staticmethod
    def _send_employee_created_email_sync(
        to_email: str, employee_name: str
    ) -> None:
        message = EmailMessage()
        message["Subject"] = "Your employee account has been created"
        message["From"] = settings.MAIL_FROM
        message["To"] = to_email
        message.set_content(
            f"Hello {employee_name},\n\n"
            "Your employee record has been created successfully."
        )

        if settings.SMTP_PORT == 465:
            connection = smtplib.SMTP_SSL(
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                context=ssl.create_default_context(),
                timeout=SMTP_TIMEOUT_SECONDS,
            )
        else:
            connection = smtplib.SMTP(
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                timeout=SMTP_TIMEOUT_SECONDS,
            )

        with connection as smtp:
            if settings.SMTP_PORT != 465:
                smtp.starttls(context=ssl.create_default_context())
            smtp.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD.get_secret_value(),
            )
            smtp.send_message(message)
