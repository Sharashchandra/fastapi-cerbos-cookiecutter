import inspect
import os

from jinja2 import BaseLoader, Environment
from loguru import logger

from src.core.config import config
from src.core.helpers.email import EmailHelper
from src.core.helpers.rq import queue


class EmailBase:
    """Base class for email-related operations."""

    def get_template(self) -> str:
        """
        Read and return the contents of a template file.

        Args:
            template_file_path (str): Path to the template file.

        Returns:
            str: Contents of the template file.
        """
        if self.__class__.__name__ == "EmailBase":
            raise NotImplementedError("Need to invoke the function on the inherited class")

        file_path = inspect.getfile(self.__class__)
        template_file_path = os.path.join(os.path.dirname(file_path), "template.html")
        with open(template_file_path, "r") as f:
            template = f.read()

        return template

    def get_subject(self) -> str:
        """
        Get the subject of the email.

        Returns:
            str: The subject of the email.
        """
        return getattr(self.__class__, "subject", self.__class__.__name__)

    def render_template(self, template: str, config: dict) -> str:
        """
        Render the given template with the provided configuration.

        Args:
            template (str): The template string to render.
            config (dict): The configuration dictionary for template rendering.

        Returns:
            str: The rendered template.
        """
        logger.info(f"[{self.__class__.__name__}] Rendering template")
        validated_data = {}
        if schema := getattr(self.__class__, "schema", None):
            logger.info(f"[{self.__class__.__name__}] Validating config")
            validated_data = schema.model_validate(config)
            validated_data = validated_data.model_dump(mode="json")

        env = Environment(loader=BaseLoader())
        jinja_template = env.from_string(template)
        rendered_template = jinja_template.render(**validated_data)

        return rendered_template

    def get_rendered_template(self, config: dict) -> str:
        """
        Get and render the template with the provided configuration.

        Args:
            config (dict): The configuration dictionary for template rendering.

        Returns:
            str: The rendered template.
        """
        template = self.get_template()
        rendered_template = self.render_template(template, config)

        return rendered_template

    @classmethod
    def send_email(
        cls,
        email_to: str | list[str],
        body_config: dict | None = None,
        attachments: list[dict[str, str]] | None = None,
    ):
        """
        Send an email with the specified parameters.

        Args:
            email_from (str): Sender's email address.
            email_to (str | list[str]): Recipient email address(es).
            body_config (dict): Configuration for rendering the email body template.
            attachments (list[dict[str,str]] | None, optional): List of s3 paths to attach. Defaults to None.

        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        self = cls()
        body = self.get_rendered_template(body_config or {})
        email_subject = self.get_subject()
        email_to = [email_to] if isinstance(email_to, str) else email_to

        queue.enqueue(
            EmailHelper().send_email,
            email_from=config.SMTP_EMAIL_FROM,
            email_to=email_to,
            email_subject=email_subject,
            email_body=body,
            attachments=attachments,
        )
