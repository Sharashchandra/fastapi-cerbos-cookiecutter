from email.mime.multipart import MIMEMultipart

import boto3
from loguru import logger


class SESHelper:
    """Helper class for sending emails using Amazon SES."""

    def __init__(self):
        self.client = boto3.client("ses")

    def send_email(
        self,
        email_from: str,
        email_to: str | list[str],
        email_body: MIMEMultipart,
    ):
        """
        Send an email using Amazon SES.

        Args:
            email_from (str): The sender's email address.
            email_to (str | list[str]): The recipient's email address or a list of addresses.
            email_body (MIMEMultipart): The email body as a MIMEMultipart object.

        Returns:
            dict: The response from the SES send_raw_email API call.
        """
        logger.info(f"Sending email to {email_to} via AWS SES")
        response = self.client.send_raw_email(
            Source=email_from,
            Destinations=email_to,
            RawMessage={"Data": email_body.as_string()},
        )

        return response
