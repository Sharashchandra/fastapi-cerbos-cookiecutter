from datetime import datetime, timedelta, timezone

from loguru import logger

from src.core.config import config
from src.core.constants import TokenType
from src.core.helpers.redis import cache
from src.database.session import AsyncSessionLocal
from src.users.crud import crud_blacklisted_token
from src.users.models import BlacklistedToken


class PreloadBlacklistedTokens:
    cache_key_prefix = "blacklist"

    def __init__(self):
        self.log_prefix = f"[{self.__class__.__name__}]"

    async def preload_blacklisted_refresh_tokens(self):
        blacklisted_refresh_token_filters = [
            BlacklistedToken.token_type == TokenType.REFRESH,
            BlacklistedToken.blacklisted_on
            > (datetime.now(timezone.utc) - timedelta(minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES)),
        ]
        async with AsyncSessionLocal() as db:
            blacklisted_refresh_tokens = await crud_blacklisted_token.filter(
                db, filters=blacklisted_refresh_token_filters
            )
        logger.info(f"Preloading {len(blacklisted_refresh_tokens)} blacklisted refresh tokens into cache")

        for token in blacklisted_refresh_tokens:
            cache_key = f"{self.cache_key_prefix}:refresh:{token.token}"
            expiry_seconds = datetime.now(timezone.utc) - token.blacklisted_on
            logger.debug(f"Setting {cache_key} for {expiry_seconds} seconds")
            cache.setex(name=cache_key, time=expiry_seconds.seconds, value=str(True))

    async def preload_blacklisted_reset_password_tokens(self):
        blacklisted_reset_password_token_filters = [
            BlacklistedToken.token_type == TokenType.RESET_PASSWORD,
            BlacklistedToken.blacklisted_on
            > (datetime.now(timezone.utc) - timedelta(minutes=config.RESET_PASSWORD_TOKEN_EXPIRY_MINUTES)),
        ]
        async with AsyncSessionLocal() as db:
            blacklisted_reset_password_tokens = await crud_blacklisted_token.filter(
                db, filters=blacklisted_reset_password_token_filters
            )
        logger.info(f"Preloading {len(blacklisted_reset_password_tokens)} blacklisted reset password tokens into cache")

        for token in blacklisted_reset_password_tokens:
            cache_key = f"{self.cache_key_prefix}:reset_password:{token.token}"
            expiry_seconds = datetime.now(timezone.utc) - token.blacklisted_on
            logger.debug(f"Setting {cache_key} for {expiry_seconds} seconds")
            cache.setex(name=cache_key, time=expiry_seconds.seconds, value=str(True))

    async def preload_blacklisted_tokens(self):
        await self.preload_blacklisted_refresh_tokens()
        await self.preload_blacklisted_reset_password_tokens()

    async def run(self):
        # Delete all existing blacklisted tokens
        logger.info(f"{self.log_prefix} Purging all existing blacklisted tokens from the cache")
        for key in cache.scan_iter(f"{self.cache_key_prefix}:*"):
            cache.delete(key)

        logger.info(f"{self.log_prefix} Starting to preload blacklisted tokens into the cache")
        await self.preload_blacklisted_tokens()
        logger.info("Preloaded blacklisted tokens into the cache")
