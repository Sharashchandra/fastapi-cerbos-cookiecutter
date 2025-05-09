from pydantic import AnyHttpUrl, BaseModel

from src.core.config import config
from src.notifications.email.base import EmailBase


class MFAConfigSchema(BaseModel):
    token: str
    expiry_minutes: int = config.TOKEN_EXPIRY_MINUTES
    reset_password_url: AnyHttpUrl | None = None


class MFAEmail(EmailBase):
    schema = MFAConfigSchema
    subject = "Your Login Verification Code"
