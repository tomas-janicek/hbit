from dataclasses import dataclass


@dataclass
class SendEmail:
    email_to: str
    subject: str
    html_content: str


class FakeEmailSender:
    def __init__(self):
        self.send_emails: list[SendEmail] = []

    def send_email(
        self,
        *,
        email_to: str,
        subject: str = "",
        html_content: str = "",
    ) -> None:
        send_email = SendEmail(
            email_to=email_to,
            subject=subject,
            html_content=html_content,
        )
        self.send_emails.append(send_email)
