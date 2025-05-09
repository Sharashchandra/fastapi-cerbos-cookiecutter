import os
from datetime import datetime, timezone
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.authentication.exceptions import (
    InvalidCredentialsException,
    TokenExpiredException,
    UserInactiveOrBlockedException,
)
from src.authentication.services.mfa import MFAService
from src.core.config import config
from src.core.constants import TokenType
from src.core.helpers.redis import cache
from src.core.security.passwords import Password
from src.core.security.tokens import Tokens
from src.notifications.email.reset_password.reset_password import ResetPasswordEmail
from src.users.crud import crud_blacklisted_token, crud_user
from src.users.exceptions import UserNotFoundException
from src.users.models import BlacklistedToken, User


class AuthenticationHelper:
    @staticmethod
    def generate_tokens(user: User, issue_refresh_token: bool = True) -> dict:
        tokens = {"access_token": Tokens.create_access_token(data={"user_id": str(user.id)})}
        if issue_refresh_token:
            tokens["refresh_token"] = Tokens.create_refresh_token(data={"user_id": str(user.id)})

        return tokens

    @staticmethod
    def generate_reset_password_link(user: User) -> str:
        reset_password_token = Tokens.create_reset_password_token(data={"email": user.email})

        base_url = os.path.join(config.PROJECT_BASE_URL.unicode_string(), config.API_PREFIX)
        reset_password_url = os.path.join(base_url, f"auth/set-password/?token={reset_password_token}")

        return reset_password_url

    @staticmethod
    async def blacklist_token_in_db(db: AsyncSession, user_id: UUID, token: str, token_type: TokenType):
        blacklist_token = BlacklistedToken(
            token=token,
            token_type=token_type,
            blacklisted_on=datetime.now(timezone.utc),
            created_by_id=user_id,
        )

        await crud_blacklisted_token.create_obj(db, obj=blacklist_token)

    @staticmethod
    def blacklist_token_in_cache(token: str, token_type: TokenType):
        cache_key = f"blacklist:{token_type.value}:{token}"
        expiry_seconds = config.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        cache.setex(name=cache_key, time=expiry_seconds, value=str(True))

    @staticmethod
    async def blacklist_token(db: AsyncSession, user_id: UUID, token: str, token_type: TokenType):
        await AuthenticationHelper.blacklist_token_in_db(db, user_id=user_id, token=token, token_type=token_type)
        AuthenticationHelper.blacklist_token_in_cache(token=token, token_type=token_type)


class AuthenticationService(AuthenticationHelper):
    @classmethod
    async def login(cls, db: AsyncSession, email: str, password: str) -> User:
        user = await crud_user.get_by_filters(db, filters=[User.email == email])
        if not user:
            raise InvalidCredentialsException()

        # Verify password
        if not Password.verify_password(plain_password=password, hashed_password=user.password):
            raise InvalidCredentialsException()

        if not user.is_active:
            logger.info(f"<User: {user.email}> is inactive")
            raise UserInactiveOrBlockedException()

        if user.is_blocked:
            logger.info(f"<User: {user.email}> is blocked until {user.blocked_until}")
            raise UserInactiveOrBlockedException()

        if not user.is_mfa_enabled:
            user.last_login = datetime.now(timezone.utc)
            await crud_user.update_obj(db, obj=user)
            await db.commit()
            return cls.generate_tokens(user=user)

        # Generate mfa attempt
        await MFAService.generate_mfa_attempt(db, user=user)
        return {"message": "Login successful. You'll recieve a token on your registered mail id"}

    @classmethod
    async def verify_token(cls, db: AsyncSession, email: str, token: str) -> dict:
        user = await crud_user.get_by_filters(db, filters=[User.email == email])
        if not user:
            raise InvalidCredentialsException()

        MFAService.verify_token(db, user=user, token=token)
        user.last_login = datetime.now(timezone.utc)
        user.active_mfa_attempt = None
        await crud_user.update_obj(db, obj=user)
        await db.commit()

        return cls.generate_tokens(user=user)

    @classmethod
    async def reissue_access_token(cls, user: User, refresh_token: str) -> dict:
        cache_key = f"blacklist:{TokenType.REFRESH.value}:{refresh_token}"
        if cache.get(cache_key):
            raise TokenExpiredException()

        return cls.generate_tokens(user=user, issue_refresh_token=False)

    @classmethod
    async def init_reset_password(cls, db: AsyncSession, email: str) -> dict:
        # TODO: Need to allow initialization of reset password only once
        user = await crud_user.get_by_filters(db, filters=[User.email == email])
        if user:
            reset_password_link = cls.generate_reset_password_link(user=user)
            ResetPasswordEmail.send_email(email_to=user.email, body_config={"reset_password_url": reset_password_link})

        return {
            "message": "If the provided email is associated with an active user, a reset password link will been sent to your email. Please check your email for further instructions."
        }

    @classmethod
    async def reset_password(cls, db: AsyncSession, token: str, email: str, password: str) -> dict:
        user = await crud_user.get_by_filters(db, filters=[User.email == email])
        if not user:
            raise UserNotFoundException()

        if cache.get(f"blacklist:{TokenType.RESET_PASSWORD.value}:{token}"):
            raise TokenExpiredException(
                detail="The provided link has already been used to reset your password. Please request a new link."
            )

        user.password = Password.get_hashed_password(password)
        await crud_user.update_obj(db, obj=user)
        await cls.blacklist_token(db, user_id=user.id, token=token, token_type=TokenType.RESET_PASSWORD)
        await db.commit()

        return {"message": "Password reset successfully, you can now login with your new password"}

    @classmethod
    async def logout(cls, db: AsyncSession, refresh_token: str, user_id: UUID) -> dict:
        await cls.blacklist_token(db, user_id=user_id, token=refresh_token, token_type=TokenType.REFRESH)
        await db.commit()

        return {"message": "You have been logged out successfully"}
