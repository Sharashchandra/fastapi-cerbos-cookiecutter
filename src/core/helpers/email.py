import os
import tempfile
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger


class EmailHelper:
    def send_email_via_ses(
        self,
        email_from: str,
        email_to: list[str],
        email_body: MIMEMultipart,
    ):
        """
        Send an email using Amazon SES.

        Args:
            email_from (str): The sender's email address.
            email_to (list[str]): A list of recipient email addresses.
            email_body (MIMEMultipart): The email body as a MIMEMultipart object.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        from src.core.helpers.ses import SESHelper

        return SESHelper().send_email(
            email_from=email_from,
            email_to=email_to,
            email_body=email_body,
        )

    def send_email_via_smtp(
        self,
        email_from: str,
        email_to: list[str],
        email: MIMEMultipart,
    ):
        """
        Send an email using SMTP.

        Args:
            email_from (str): The sender's email address.
            email_to (list[str]): A list of recipient email addresses.
            email (MIMEMultipart): The email message as a MIMEMultipart object.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        from src.core.helpers.smtp import SMTPHelper

        return SMTPHelper().send_email(
            email_from=email_from,
            email_to=email_to,
            email_body=email,
        )

    def handle_file_attachment(self, temp_dir: str, attachment: dict) -> MIMEApplication:
        """
        Handle file attachments for email.

        Args:
            temp_dir (str): Temporary directory to store downloaded files.
            attachment (dict): Dictionary containing file attachment information.
                Example:
                {
                    "type": "file",
                    "file_path": "/file/path",
                    "file_name" (optional): "file_name.csv"
                }

        Returns:
            MIMEApplication: MIME attachment for the email.
        """
        file_path = attachment.get("file_path", "")
        file_name = attachment.get("file_name") or os.path.basename(file_path)
        with open(file_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=file_name)
            part.add_header("Content-Disposition", "attachment", filename=file_name)

        return part

    def handle_s3_attachment(self, temp_dir: str, attachment: dict) -> MIMEApplication:
        """
        Handle S3 attachments for email.

        Args:
            temp_dir (str): Temporary directory to store downloaded files.
            attachment (dict): Dictionary containing S3 attachment information.
                Example:
                {
                    "type": "s3",
                    "s3_uri": "s3://bucket/key",
                    "file_name" (optional): "file_name.csv"
                }

        Returns:
            MIMEApplication: MIME attachment for the email.
        """
        from src.core.helpers.s3 import S3Helper

        file_path = S3Helper().download_file(
            local_dir_path=temp_dir,
            s3_uri=attachment["s3_uri"],
        )
        file_name = attachment.get("file_name") or os.path.basename(file_path)
        with open(file_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=file_name)
            part.add_header("Content-Disposition", "attachment", filename=file_name)

        return part

    def get_attachments(self, temp_dir: str, attachments: list[dict[str, str]]) -> list[MIMEApplication]:
        """
        Process a list of attachments and return a list of MIMEApplication objects.

        Args:
            temp_dir (str): Temporary directory to store downloaded files.
            attachments (list[dict[str, str]]): List of attachment dictionaries.

        Returns:
            list[MIMEApplication]: List of MIME attachments for the email.
        """
        mime_applications = []
        for attachment in attachments:
            func = None
            match attachment.get("type"):
                case "s3":
                    func = self.handle_s3_attachment
                case "file":
                    func = self.handle_file_attachment
            part = func(temp_dir, attachment)
            mime_applications.append(part)

        return mime_applications

    def send_email(
        self,
        email_from: str,
        email_to: list[str],
        email_subject: str,
        email_body: str,
        attachments: list[dict[str, str]] | None = None,
    ):
        """
        Send an email with optional attachments.

        Args:
            email_from (str): The sender's email address.
            email_to (list[str]): A list of recipient email addresses.
            email_subject (str): The subject of the email.
            email_body (str): The HTML body of the email.
            attachments (list[dict[str, str]] | None, optional): List of s3 paths to attach. Defaults to None.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        msg = MIMEMultipart()
        msg["From"] = email_from
        msg["To"] = ", ".join(email_to)
        msg["Subject"] = email_subject

        msg.attach(MIMEText(email_body, "html"))

        if attachments:
            with tempfile.TemporaryDirectory() as temp_dir:
                mime_applications = self.get_attachments(temp_dir, attachments)
                for mime_application in mime_applications:
                    msg.attach(mime_application)

        try:
            return self.send_email_via_smtp(email_from, email_to, msg)
        except Exception as e:
            logger.error(f"Error sending email via smtp: {e}")
            logger.error("Falling back to ses")
            return self.send_email_via_ses(email_from, email_to, msg)
