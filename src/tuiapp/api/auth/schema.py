"""Pydantic schemas for authentication API requests and responses."""

from enum import Enum

from pydantic import BaseModel, EmailStr

from tuiapp.api.schema import Result


class RoleID(Enum):
    """Enum representing user role identifiers.

    Attributes:
        USER: Regular user role (value 3).
        MODERATOR: Moderator role (value 2).
        ADMIN: Administrator role (value 1).
    """

    USER = 3
    MODERATOR = 2
    ADMIN = 1


class Token(BaseModel):
    """Response model containing access and refresh tokens.

    Attributes:
        access_token: The JWT access token for API requests.
        refresh_token: The token used to obtain new access tokens.
        token_type: The type of token (default: bearer).
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Request model for user login.

    Attributes:
        email: The user's email address.
        password: The user's password.
    """

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Request model for token refresh.

    Attributes:
        refresh_token: The refresh token to use for obtaining new access token.
    """

    refresh_token: str


class TokenResult(Result):
    """Result model for authentication operations.

    Attributes:
        token: The Token object on success, None on failure.
        message: A descriptive message about the result.
        status: The status of the operation (success, invalid, or error).
    """

    token: Token | None


"""Pydantic schemas for account API requests and responses."""


class User(BaseModel):
    """Response model for current user information.

    Attributes:
        firstname: The user's first name.
        lastname: The user's last name.
        email: The user's email address.
        id: The unique identifier of the user.
        role_id: The user's role identifier.
        is_active: Whether the user account is active.
    """

    firstname: str
    lastname: str
    email: EmailStr
    id: int
    role_id: RoleID
    is_active: bool


class UserResult(Result):
    """Result model for user-related operations.

    Extends Result to include user data on successful operations.

    Attributes:
        message: A descriptive message about the result.
        status: The status of the operation (success, invalid, or error).
        user: The User object on success, None on failure.
    """

    user: User | None
