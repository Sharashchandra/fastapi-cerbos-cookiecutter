from pydantic import BaseModel, EmailStr, SecretStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class VerifyTokenSchema(BaseModel):
    email: EmailStr
    token: str


class ResetPasswordSchema(BaseModel):
    email: EmailStr


class SetPasswordSchema(BaseModel):
    password: SecretStr


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class LogoutSchema(RefreshTokenSchema): ...
