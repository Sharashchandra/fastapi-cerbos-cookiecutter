import secrets
import string
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio.session import AsyncSession

from src.authentication.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    TokenNotGeneraetdException,
    UserInactiveOrBlockedException,
)
from src.core.config import config
from src.notifications.email.mfa.mfa import MFAEmail
from src.users.crud import crud_mfa_attempt, crud_user
from src.users.models import MFAAttempt, User


class MFAHelper:
    @staticmethod
    def generate_random_token() -> str:
        alphabet = string.ascii_letters + string.digits
        token = "".join(secrets.choice(alphabet) for _ in range(config.TOKEN_LENGTH))

        return token

    @staticmethod
    async def handle_token_expiry(db: AsyncSession, user: User):
        if datetime.now(timezone.utc) < user.active_mfa_attempt.code_expires_at:
            return

        user.active_mfa_attempt = None
        await crud_user.update_obj(db, obj=user)
        await db.commit()
        raise TokenExpiredException()

    @staticmethod
    async def handle_invalid_token(db: AsyncSession, user: User):
        user.active_mfa_attempt.incorrect_attempts_count += 1

        if user.active_mfa_attempt.incorrect_attempts_count >= config.MAX_INCORRECT_ATTEMPTS:
            user.is_blocked = True
            user.blocked_until = datetime.now(timezone.utc) + timedelta(minutes=config.BLOCKED_USER_DURATION_MINUTES)
            user.active_mfa_attempt = None
            await crud_user.update_obj(db, obj=user)
            await db.commit()
            raise UserInactiveOrBlockedException(
                detail=f"Maximum invalid attempts reached. User blocked for {config.BLOCKED_USER_DURATION_MINUTES} minutes."
            )

        await crud_mfa_attempt.update_obj(db, obj=user.active_mfa_attempt)
        await db.commit()
        raise InvalidTokenException()


class MFAService(MFAHelper):
    @classmethod
    async def reset_mfa_attempt(cls, db: AsyncSession, user: User):
        user.active_mfa_attempt = None
        await crud_user.update_obj(db, obj=user)

        await db.commit()

    @classmethod
    async def generate_mfa_attempt(cls, db: AsyncSession, user: User) -> None:
        token = cls.generate_random_token()
        code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=config.TOKEN_EXPIRY_MINUTES)
        mfa_attempt = MFAAttempt(user_id=user.id, code=token, code_expires_at=code_expires_at)

        await crud_mfa_attempt.create_obj(db, obj=mfa_attempt)
        await db.commit()

        # Send mfa email
        MFAEmail.send_email(email_to=user.email, body_config={"token": token})

    @classmethod
    async def verify_token(cls, db: AsyncSession, user: User, token: str) -> None:
        # Validate MFA attempt exists
        if not user.active_mfa_attempt:
            raise TokenNotGeneraetdException()

        await cls.handle_token_expiry(db, user=user)

        # Verify token
        if user.active_mfa_attempt.code == token:
            return

        await cls.handle_invalid_token(db, user=user)
