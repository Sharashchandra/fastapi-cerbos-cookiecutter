from pydantic import AnyHttpUrl, BaseModel

from src.notifications.email.base import EmailBase


class ResetPasswordSchema(BaseModel):
    reset_password_url: AnyHttpUrl


class ResetPasswordEmail(EmailBase):
    schema = ResetPasswordSchema
    subject = "Reset password instructions"
