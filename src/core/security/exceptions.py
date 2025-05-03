from typing import Any

from fastapi import HTTPException, status


class InvalidOrExpiredTokenException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Any = "The provided token is either invalid or expired.",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class InvalidTokenTypeException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: Any = "The provided token type is invalid.",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
