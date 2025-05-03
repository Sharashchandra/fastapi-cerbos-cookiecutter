import smtplib
from email.mime.multipart import MIMEMultipart

from loguru import logger

from src.core.config import config


class SMTPHelper:
    def send_email(
        self,
        email_from: str,
        email_to: list[str],
        email_body: MIMEMultipart,
    ) -> bool:
        """
        Send an email using SMTP.

        Args:
            email_from (str): The sender's email address.
            email_to (list[str]): A list of recipient email addresses.
            email_body (MIMEMultipart): The email body as a MIMEMultipart object.

        Returns:
            bool: True if the email was sent successfully, False otherwise.

        Raises:
            smtplib.SMTPException: If there's an error during the SMTP operation.
        """
        logger.info(f"Sending email to {email_to} via SMTP")
        try:
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
                server.starttls()
                server.login(
                    config.SMTP_USERNAME,
                    config.SMTP_PASSWORD.get_secret_value(),
                )
                server.send_message(
                    msg=email_body,
                    from_addr=email_from,
                    to_addrs=email_to,
                )
            return True
        except smtplib.SMTPException as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
