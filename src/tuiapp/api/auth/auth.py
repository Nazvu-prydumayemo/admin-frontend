"""Authentication service for handling login, registration, and user information."""

from tuiapp.api.auth.schema import (
    LoginRequest,
    RoleID,
    Token,
    TokenResult,
    User,
    UserResult,
)
from tuiapp.api.client import APIClient
from tuiapp.api.errors import APIError


class AuthService:
    """Service for handling authentication operations.

    Provides methods for user login, registration, and retrieving current user
    information via the backend API.

    Attributes:
        _client: The API client used for making HTTP requests.
    """

    def __init__(self, client: APIClient) -> None:
        """Initialize the AuthService with an API client.

        Args:
            client: The APIClient instance for making authenticated requests.
        """
        self._client = client

    async def login(self, json: LoginRequest) -> TokenResult:
        """Authenticate a user with email and password.

        Args:
            json: The login credentials containing email and password.

        Returns:
            TokenResult containing the access/refresh tokens on success,
            or an error message with status indicator on failure.
        """
        try:
            token = await self._client.post("/auth/login", json=json, response_model=Token)
            self._client.set_access_token(token.access_token)

            user = (await self.me()).user
            if user is None:
                self._client.set_access_token(None)
                raise APIError(status_code=401, message="Invalid username or password")

            if user.role_id != RoleID.ADMIN:
                self._client.set_access_token(None)
                raise APIError(status_code=403, message="Entry is forbidden")

            self._client.set_access_token(None)
            return TokenResult(token=token, message="Login successful", status="success")

        except APIError as error:
            if error.status_code in (400, 401, 422):
                return TokenResult(
                    token=None, message="Invalid username or password", status="invalid"
                )

            if error.status_code == 403:
                return TokenResult(token=None, message=error.message, status="invalid")

            else:
                return TokenResult(
                    token=None, message=f"Server error: {error.status_code}", status="error"
                )

    async def me(self) -> UserResult:
        """Fetch the current user's profile information.

        Calls the /account/me endpoint to retrieve the authenticated user's
        details including firstname, lastname, email, and account status.

        Returns:
            UserResult: Contains the user data on success, or error status and message on failure.
        """
        try:
            response = await self._client.get("/account/me", User)
            return UserResult(user=response, message="Authenticated", status="success")

        except APIError as error:
            if error.status_code == 401:
                return UserResult(user=None, message="Not Authenticated", status="invalid")

            return UserResult(
                user=None, message=f"Server error: {error.status_code}", status="error"
            )
