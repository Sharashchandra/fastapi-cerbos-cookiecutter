from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import status
from jwt.exceptions import PyJWTError

from src.core.config import config
from src.core.constants import TokenType
from src.core.security.exceptions import InvalidOrExpiredTokenException, InvalidTokenTypeException


class Tokens:
    @classmethod
    def create_token(cls, token_type: str, expires_delta: timedelta | None = None, data: dict | None = None) -> str:
        """
        Create an token of the given type with the given data and expiration time.

        Args:
            token_type (str): The type of the token.
            expires_delta (timedelta): The expiration time for the token.
            data (dict): The data to be encoded in the token.

        Returns:
            str: The encoded JWT access token.
        """
        data = data or {}
        to_encode = data.copy()
        issued_at = datetime.now(timezone.utc)
        jti = uuid4().hex
        expire = issued_at + expires_delta
        to_encode.update({"token_type": token_type, "iat": issued_at, "exp": expire, "jti": jti})
        encoded_jwt = jwt.encode(
            payload=to_encode,
            key=config.JWT_SECRET_KEY.get_secret_value(),
            algorithm=config.JWT_ALGORITHM,
        )

        return encoded_jwt

    @classmethod
    def create_access_token(cls, data: dict | None = None, expires_delta: timedelta | None = None) -> str:
        """
        Create an access token with the given data and expiration time.

        Args:
            data (dict): The data to be encoded in the token.
            expires_delta (timedelta | None): The expiration time for the token.

        Returns:
            str: The encoded JWT access token.
        """
        return cls.create_token(
            token_type=TokenType.ACCESS.value,
            expires_delta=expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
            data=data,
        )

    @classmethod
    def create_refresh_token(cls, data: dict | None = None, expires_delta: timedelta | None = None) -> str:
        """
        Create a refresh token with the given expiration time.

        Args:
            expires_delta (timedelta | None): The expiration time for the token.

        Returns:
            str: The encoded JWT refresh token.
        """
        return cls.create_token(
            token_type=TokenType.REFRESH.value,
            expires_delta=expires_delta or timedelta(days=config.REFRESH_TOKEN_EXPIRE_MINUTES),
            data=data,
        )

    @classmethod
    def create_reset_password_token(cls, data: dict | None = None, expires_delta: timedelta | None = None) -> str:
        """
        Create a reset password token with the given data and expiration time.

        Args:
            data (dict): The data to be encoded in the token.
            expires_delta (timedelta | None): The expiration time for the token.

        Returns:
            str: The encoded JWT reset password token.
        """
        return cls.create_token(
            token_type=TokenType.RESET_PASSWORD.value,
            expires_delta=expires_delta or timedelta(minutes=config.RESET_PASSWORD_TOKEN_EXPIRY_MINUTES),
            data=data,
        )

    @classmethod
    def decode_token(cls, token: str) -> dict:
        """
        Decode and verify the given JWT token.

        Args:
            token (str): The JWT token to decode.

        Returns:
            dict: The decoded token claims.
        """
        return jwt.decode(
            jwt=token,
            key=config.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[config.JWT_ALGORITHM],
            options={"require_exp": True, "require_jti": True, "require_iat": True},
        )

    @classmethod
    def verify_token(cls, token: str):
        try:
            payload = cls.decode_token(token=token)
            if payload["token_type"] not in [TokenType.ACCESS.value, TokenType.REFRESH.value]:
                raise InvalidTokenTypeException(status_code=status.HTTP_403_FORBIDDEN)
            if payload["token_type"] == TokenType.ACCESS.value and "user_id" not in payload:
                raise InvalidOrExpiredTokenException(status_code=status.HTTP_403_FORBIDDEN)
            return payload
        except PyJWTError as error:
            raise InvalidOrExpiredTokenException(status_code=status.HTTP_401_UNAUTHORIZED) from error

    @classmethod
    def verify_reset_password_token(cls, token: str):
        try:
            payload = cls.decode_token(token=token)
            if payload["token_type"] != TokenType.RESET_PASSWORD.value:
                raise InvalidTokenTypeException()
            if "email" not in payload:
                raise InvalidOrExpiredTokenException(status_code=status.HTTP_403_FORBIDDEN)
            return payload
        except PyJWTError as error:
            raise InvalidOrExpiredTokenException(status_code=status.HTTP_401_UNAUTHORIZED) from error
