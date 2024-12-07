import logging
import typing

import emails  # type: ignore
from jinja2 import Template

from hbit_api.core.config import settings

_log = logging.getLogger(__name__)


class BaseEmailSender:
    def send_email(
        self,
        *,
        email_to: str,
        subject: str = "",
        html_content: str = "",
    ) -> None: ...


class EmailSender(BaseEmailSender):
    def __init__(self) -> None:
        self.smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
        if settings.SMTP_TLS:
            self.smtp_options["tls"] = True
        elif settings.SMTP_SSL:
            self.smtp_options["ssl"] = True
        if settings.SMTP_USER:
            self.smtp_options["user"] = settings.SMTP_USER
        if settings.SMTP_PASSWORD:
            self.smtp_options["password"] = settings.SMTP_PASSWORD

    def send_email(
        self,
        *,
        email_to: str,
        subject: str = "",
        html_content: str = "",
    ) -> None:
        assert settings.emails_enabled, "no provided configuration for email variables"
        message = emails.Message(
            subject=subject,
            html=html_content,
            mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
        )

        response = message.send(to=email_to, smtp=self.smtp_options)  # type: ignore
        _log.info(f"send email result: {response}")

    @staticmethod
    def render_email_template(
        *, template_name: str, context: dict[str, typing.Any]
    ) -> str:
        template_str = (
            settings.BASE_DIR / "email-templates" / "build" / template_name
        ).read_text()
        html_content = Template(template_str).render(context)
        return html_content
