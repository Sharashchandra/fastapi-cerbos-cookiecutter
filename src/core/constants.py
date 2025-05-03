from enum import Enum


class Environment(str, Enum):
    """
    An enumeration representing the various environments in which the application can run.
    Attributes:
        LOCAL: Represents a local development environment on a developer's machine.
        DEVELOPMENT: Represents a shared development environment where developers test their code together.
        QA: Represents a Quality Assurance environment for dedicated testing.
        UAT: Represents a User Acceptance Testing environment for final testing by users.
        PRODUCTION: Represents the final environment where the application is available to end users.
    """

    LOCAL = "local"
    DEVELOPMENT = "dev"
    QA = "qa"
    UAT = "uat"
    PRODUCTION = "prod"


class TokenType(str, Enum):
    """
    An enumeration representing the various types of tokens in the application.
    Attributes:
        ACCESS: Represents an access token used for authentication and authorization.
        REFRESH: Represents a refresh token used to obtain new access tokens.
        RESET_PASSWORD: Represents a token used to reset the password of a user.
    """

    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
