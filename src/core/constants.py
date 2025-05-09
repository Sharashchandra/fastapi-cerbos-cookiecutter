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


class UserRoles(str, Enum):
    """
    An enumeration representing the various roles that a user can have.
    Attributes:
        ADMIN: Represents an administrator role.
        USER: Represents a user role.
    """

    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    USER = "user"


class ResourceActions(str, Enum):
    """
    An enumeration representing the various actions that can be performed on resources.
    Attributes:
        LIST: Represents the action of listing resources.
        GET: Represents the action of reading an existing resource.
        CREATE: Represents the action of creating a new resource.
        UPDATE: Represents the action of updating an existing resource.
        DELETE: Represents the action of deleting an existing resource.
    """

    LIST = "list"
    GET = "get"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
