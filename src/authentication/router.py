from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.authentication.schemas import (
    LoginSchema,
    LogoutSchema,
    RefreshTokenSchema,
    ResetPasswordSchema,
    SetPasswordSchema,
    VerifyTokenSchema,
)
from src.authentication.services.authentication import AuthenticationService
from src.core.security.dependencies import verify_http_token, verify_reset_password_token
from src.database.dependencies import get_db

authentication_router = APIRouter(prefix="/auth", tags=["Authentication"])


@authentication_router.post("/login/", status_code=status.HTTP_200_OK)
async def login(creds: LoginSchema, db: AsyncSession = Depends(get_db)) -> dict:
    return await AuthenticationService.login(
        db,
        email=creds.email,
        password=creds.password,
    )


@authentication_router.post("/verify-token/", status_code=status.HTTP_202_ACCEPTED)
async def verify_token(token_data: VerifyTokenSchema, db: AsyncSession = Depends(get_db)) -> dict:
    return await AuthenticationService.verify_token(
        db,
        email=token_data.email,
        token=token_data.token,
    )


@authentication_router.post("/refresh/", status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_token_data: RefreshTokenSchema,
    token_payload: dict = Depends(verify_http_token),
) -> dict:
    return await AuthenticationService.reissue_access_token(
        user_id=token_payload["user_id"],
        refresh_token=refresh_token_data.refresh_token,
    )


@authentication_router.post("/reset-password/", status_code=status.HTTP_202_ACCEPTED)
async def reset_password(reset_password_data: ResetPasswordSchema, db: AsyncSession = Depends(get_db)) -> dict:
    return await AuthenticationService.init_reset_password(
        db,
        email=reset_password_data.email,
    )


@authentication_router.post("/set-password/", status_code=status.HTTP_200_OK)
async def set_password(
    set_password_data: SetPasswordSchema,
    db: AsyncSession = Depends(get_db),
    reset_password_token_payload: dict = Depends(verify_reset_password_token),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> dict:
    return await AuthenticationService.reset_password(
        db,
        token=credentials.credentials,
        email=reset_password_token_payload["email"],
        password=set_password_data.password,
    )


@authentication_router.post("/logout/", status_code=status.HTTP_200_OK)
async def logout(
    logout_data: LogoutSchema,
    db: AsyncSession = Depends(get_db),
    token_payload: dict = Depends(verify_http_token),
) -> dict:
    return await AuthenticationService.logout(
        db,
        refresh_token=logout_data.refresh_token,
        user_id=token_payload["user_id"],
    )
