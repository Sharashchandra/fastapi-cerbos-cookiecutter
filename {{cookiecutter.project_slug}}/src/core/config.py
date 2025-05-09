from functools import lru_cache

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, SecretStr, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict

from src.core.constants import Environment


class BaseConfig(PydanticBaseSettings):
    model_config = SettingsConfigDict(
        use_enum_values=True,
        case_sensitive=True,
    )


class GeneralConfig(BaseConfig):
    PROJECT_NAME: str = "{{cookiecutter.project_name}}"

    # the endpoint prefix for api docs and all endpoints
    API_PREFIX: str = "/api"

    # List of allowed CORS origins
    ALLOWED_CORS_ORIGINS: list[AnyHttpUrl] = []
    CORS_EXPOSE_HEADERS: list[str] = []

    # Environment
    ENVIRONMENT: Environment = Environment.LOCAL

    HEALTH_CHECK_URL: str = "/api/health/app"

    PROJECT_BASE_URL: AnyHttpUrl | None = None


class DatabaseConfig(BaseConfig):
    # Database settings
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: SecretStr | None = None
    DB_HOST: str | None = None
    DB_PORT: str | None = "5432"
    DB_URL: PostgresDsn | None = None

    @field_validator("DB_URL", mode="before")
    def assemble_db_connection(cls, value: str | None, info: FieldValidationInfo) -> str:
        """
        Assemble the Postgres DB connection string (DSN).

        If DB_URL is already provided as a string, just return it.

        If DB_URL is not provided, then the other Postgres DB fields (DB_USER,
        DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME) must all be provided. Use them to
        build a Postgres DB connection string.
        """
        if value is not None and value != "":
            return value

        values = info.data
        for field in ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"]:
            if not values.get(field):
                raise ValueError(f"{field} must be set if DB_URL is not provided")

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("DB_USER"),
            password=values.get("DB_PASSWORD").get_secret_value(),
            host=values.get("DB_HOST"),
            port=int(values.get("DB_PORT")),
            path=values.get("DB_NAME"),
        )


class SMTPConfig(BaseConfig):
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: SecretStr
    SMTP_EMAIL_FROM: EmailStr


class RedisConfig(BaseConfig):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_TASK_QUEUE_DB: int


class SecurityTokenConfig(BaseConfig):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 12 * 60  # 12 hours
    RESET_PASSWORD_TOKEN_EXPIRY_MINUTES: int = 24 * 60  # 24 hours
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: SecretStr


class MFAConfig(BaseConfig):
    TOKEN_LENGTH: int = 6
    TOKEN_EXPIRY_MINUTES: int = 10
    MAX_INVALID_ATTEMPTS: int = 5
    MAX_TOKEN_REQUEST_ATTEMPTS: int = 3
    BLOCKED_USER_DURATION_MINUTES: int = 10


class CerbosConfig(BaseConfig):
    CERBOS_HOST: str | None = None
    CERBOS_PORT: int = 3593
    CERBOS_URL: str | None = None

    @field_validator("CERBOS_URL", mode="before")
    def assemble_cerbos_connection(cls, value: str | None, info: FieldValidationInfo) -> str:
        """
        Assemble the Cerbos connection string.

        If CERBOS_URL is already provided as a string, just return it.

        If CERBOS_URL is not provided, then the other Cerbos fields (CERBOS_HOST, CERBOS_PORT)
        must be provided. Use them to build a Cerbos URL
        """
        if value is not None and value != "":
            return value

        values = info.data
        if not values.get("CERBOS_HOST"):
            raise ValueError("CERBOS_HOST must be set if CERBOS_URL is not provided")

        return f"{values.get('CERBOS_HOST')}:{values.get('CERBOS_PORT')}"


class Config(
    GeneralConfig,
    DatabaseConfig,
    SMTPConfig,
    RedisConfig,
    SecurityTokenConfig,
    MFAConfig,
    CerbosConfig,
):
    pass


@lru_cache
def get_config() -> Config:  # Return the specific Config type
    return Config()


config = get_config()
