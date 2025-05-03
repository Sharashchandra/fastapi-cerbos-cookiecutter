from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.security.tokens import Tokens

security = HTTPBearer()


async def verify_http_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verifies the JWT token from the Authorization header.
    Args:
        credentials (HTTPAuthorizationCredentials): The authorization credentials.
                Defaults to Depends(security).
    Returns:
        dict: The payload of the decoded JWT token.
    Raises:
        HTTPException: If the JWT token is invalid or expired.
    """
    return Tokens.verify_token(token=credentials.credentials)


async def verify_reset_password_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verifies the JWT token from the Authorization header only for the reset password route.
    Args:
        credentials (HTTPAuthorizationCredentials): The authorization credentials.
                Defaults to Depends(security).
    Returns:
        dict: The payload of the decoded JWT token.
    Raises:
        HTTPException: If the JWT token is invalid or expired.
    """
    return Tokens.verify_reset_password_token(token=credentials.credentials)
