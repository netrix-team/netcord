import secrets

from aiohttp import BasicAuth
from urllib.parse import urlencode, quote

from fastapi import Request, Depends
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials as HTTPAuth

from netcord.http import HTTPClient
from netcord.models import Token, User, Guild
from netcord.exceptions import Unauthorized, Forbidden, ScopeMissing


class Netcord(HTTPClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        bot_token: str = None,
        redirect_uri: str = 'http://127.0.0.1/callback',
        scopes: str | list[str] = ['identify', 'email', 'guilds']
    ):
        super().__init__()

        self.client_id = client_id
        self.client_secret = client_secret

        self.bot_token = bot_token

        self.redirect_uri = redirect_uri
        self.scopes = scopes if isinstance(scopes, str) else ' '.join(scopes)

        self.state_storage = {}
        self.auth = BasicAuth(self.client_id, self.client_secret)

        self.base_url = 'https://discord.com'
        self.cdn = 'https://cdn.discordapp.com'

        self.icons = f'{self.cdn}/icons'
        self.avatars = f'{self.cdn}/avatars'
        self.banners = f'{self.cdn}/banners'

        self.api = f'{self.base_url}/api/v10'
        self.authorize = f'{self.base_url}/oauth2/authorize'

        self.token = f'{self.base_url}/api/oauth2/token'
        self.revoke = f'{self.base_url}/api/oauth2/token/revoke'

    # auth
    def generate_auth_url(self, session_id: str = None) -> str:
        """
        Generates an OAuth2 authorization URL for initiating the authorization flow with Discord.

        This method constructs the URL that users should be redirected to in order to authorize your application and grant it access to their Discord account. The URL includes necessary query parameters such as `client_id`, `redirect_uri`, `response_type`, and `scope`. Optionally, it can include a `state` parameter for maintaining state between the request and callback.

        Detailed information about the authorization URL can be found in the Discord documentation:
        https://discord.com/developers/docs/topics/oauth2#authorization-code-grant-authorization-url-example

        Parameters:
        - session_id (str, optional): An optional session identifier to associate with the state parameter. This can be used to mitigate CSRF attacks by storing the state parameter for verification during the callback phase.

        Returns:
        - str: The constructed authorization URL that users should be redirected to for initiating the OAuth2 authorization flow with Discord.

        Example:
        - The generated URL will look something like this:
            `https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=YOUR_SCOPES&state=RANDOM_STATE`

        Raises:
        - Exception: If there are any unexpected errors encountered during the URL generation.
        """

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self.scopes,
        }

        if session_id:
            state = secrets.token_urlsafe(16)
            self.state_storage[session_id] = state

            params.update({'state': state})

        return f'{self.authorize}?{urlencode(params, quote_via=quote)}'
    
    def check_state(self, session_id: str, received_state: str):
        """
        Validates the state parameter received during the OAuth2 authorization callback.

        This method checks whether the state parameter received from the authorization callback matches the stored state associated with the given session ID. This helps to protect against Cross-Site Request Forgery (CSRF) attacks by ensuring that the state parameter is valid and matches the one originally generated during the authorization URL creation.

        Detailed information about the state parameter and its usage can be found in the OAuth2 documentation:
        https://tools.ietf.org/html/rfc6749#section-10.12

        Parameters:
        - session_id (str): The session identifier associated with the state parameter.
        - received_state (str): The state parameter received from the OAuth2 authorization callback.

        Returns:
        - bool: Returns `True` if the state parameter is valid and matches the stored state; otherwise, raises an error.

        Raises:
        - Forbidden: If the state parameter does not exist for the given session ID, or if it does not match the received state. This indicates a potential CSRF attack or invalid session.
        """

        stored_state = self.state_storage.pop(session_id, None)

        if stored_state is None:
            raise Forbidden
        
        if stored_state != received_state:
            raise Forbidden
        
        return True

    async def check_token(self, request: Request) -> str | None:
        """
        Asynchronously checks and extracts the Bearer token from the Authorization header of an HTTP request.

        This method validates the presence and format of the Authorization header in the incoming HTTP request. It ensures that the header contains a Bearer token and extracts it for further use. If the header is missing or improperly formatted, an Unauthorized error is raised.

        Detailed information about the Bearer token and Authorization header can be found in the OAuth2 documentation:
        https://tools.ietf.org/html/rfc6750

        Parameters:
        - request (Request): The HTTP request object containing the headers from which the Bearer token is to be extracted.

        Returns:
        - str: The extracted Bearer token as a string if the header is valid and properly formatted.

        Raises:
        - Unauthorized: If the Authorization header is missing, does not start with 'Bearer', or is improperly formatted.
        """

        header = request.headers.get('Authorization')
        if not header:
            raise Unauthorized
        
        parts = header.split(' ')
        if parts[0] != 'Bearer' or len(parts) > 2:
            raise Unauthorized
        
        token = parts[1]
        return token

    async def login_required(self, bearer: HTTPAuth = Depends(HTTPBearer())):
        """
        Asynchronously enforces login authentication for accessing protected routes.

        This method ensures that a valid Bearer token is provided in the Authorization header of the request. It utilizes the HTTPBearer dependency to extract the token and then checks if the token corresponds to an authenticated session. If the token is missing or invalid, an Unauthorized error is raised, preventing access to the protected resource.

        Parameters:
        - bearer (HTTPAuthorizationCredentials): The Bearer token extracted from the request's Authorization header using the HTTPBearer dependency. This is automatically provided by FastAPI's dependency injection system.

        Returns:
        - None: This method does not return any value. It either allows the request to proceed if the token is valid or raises an Unauthorized error if the token is invalid.

        Raises:
        - Unauthorized: If the Bearer token is missing, invalid, or if the token does not correspond to an authenticated session.
        """

        if bearer is None:
            raise Unauthorized
        if not await self.is_authenticated(bearer.credentials):
            raise Unauthorized
        
    async def is_authenticated(self, access_token: str) -> bool:
        """
        Asynchronously checks if the provided access token is authenticated and valid.

        This method sends a request to the OAuth2 endpoint to verify the validity of the provided access token. It uses the token to make an authenticated request to the `/oauth2/@me` endpoint. If the request is successful, the token is considered valid. If the request fails with an Unauthorized error, the token is invalid or expired.

        Detailed information about the OAuth2 `/oauth2/@me` endpoint can be found in the Discord documentation:
        https://discord.com/developers/docs/topics/oauth2#get-current-authorization-information

        Parameters:
        - access_token (str): The access token to be verified for authentication.

        Returns:
        - bool: Returns `True` if the access token is valid and authenticated; otherwise, returns `False`.

        Raises:
        - Exception: For any unexpected errors encountered during the request execution.
        """

        headers = {'Authorization': 'Bearer ' + access_token}
        route = self.api + '/oauth2/@me'

        try:
            res = await self.fetch('GET', route, headers)
            print(res)

            return True
        except Unauthorized:
            return False

    # tokens
    async def _tokens(self, url: str, data: dict, return_class=None):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return await self.fetch('POST', url, headers=headers, data=data, 
                                auth=self.auth, return_class=return_class)

    async def get_access_token(self, code: str) -> Token:
        """
        Asynchronously retrieves an access token from the authentication server using an authorization code.

        This method is responsible for exchanging a provided authorization code for an access token. The access token allows the application to make authorized requests on behalf of the user. It is a critical step in the OAuth2 authentication flow, specifically the Authorization Code Grant.

        Parameters:
        - code (str): The authorization code received from the authentication server as part of the OAuth2 authorization flow. This code is exchanged for an access token.

        Returns:
        - Token: An instance of the Token class containing the access token and related information. The Token class typically includes fields such as `access_token`, `token_type`, `expires_in`, and `refresh_token`.

        Raises:
        - HTTPError: If the request to exchange the authorization code for an access token fails. This could be due to an invalid code, network issues, or server-side problems.
        - Unauthorized: If the provided authorization code is invalid or expired.
        - Exception: For any other unexpected errors encountered during the execution.
        """

        data = {
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }

        return await self._tokens(self.token, data, Token)

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Asynchronously refreshes an access token using a provided refresh token.

        This method is responsible for renewing an access token when it has expired or is about to expire, by sending a request to the authentication server with the refresh token. The refresh token is used to obtain a new access token without requiring the user to go through the authentication flow again.

        Parameters:
        - refresh_token (str): The refresh token that was issued along with the original access token. This token is used to secure a new access token.

        Returns:
        - Token: An instance of the Token class containing the new access token and related information. The Token class typically includes fields such as `access_token`, `token_type`, `expires_in`, and `refresh_token`.

        Raises:
        - HTTPError: If the request to refresh the access token fails. This could be due to an invalid or expired refresh token, network issues, or server-side problems.
        - Unauthorized: If the provided refresh token is invalid or expired.
        - Exception: For any other unexpected errors encountered during the execution.
    """

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        return await self._tokens(self.token, data, Token)

    async def revoke_access_token(self, access_token: str) -> None:
        """
        Asynchronously revokes an access token, invalidating its further use.

        This method sends a request to the authentication server to revoke an access token. Once revoked, the access token cannot be used for any further authenticated requests. This is an important feature for ensuring the security of the application, especially in scenarios where user sessions need to be terminated forcefully.

        Parameters:
        - access_token (str): The access token that needs to be revoked.

        Returns:
        - None: Indicates that the token has been successfully revoked.

        Raises:
        - HTTPError: If the request to revoke the access token fails. This could be due to network issues, server-side problems, or the token already being invalidated.
        - Unauthorized: If the access token is invalid at the time of the request.
        - Exception: For any other unexpected errors encountered during the execution.
        """

        data = {
            'token': access_token,
            'token_type_hint': 'access_token'
        }

        return await self._tokens(self.revoke, data, None)
    
    # users
    async def get_user(self, request: Request) -> User:
        """
        Asynchronously retrieves the user's profile information from the authentication server using a valid access token extracted from the request.

        This method first validates the presence of an 'Authorization' header in the provided request, extracts the access token, and checks if the required scope 'identify' is included in the initial authorization request. If the scope is missing, it raises an exception. If the scope is present, it proceeds to fetch the user data from the endpoint that provides user information.

        Parameters:
        - request (Request): The request object from which the access token will be extracted. This object must contain an 'Authorization' header with a bearer token.

        Returns:
        - User: An instance of the User class populated with the user's profile data retrieved from the server. The User class typically includes fields such as `id`, `username`, `avatar`, `discriminator`, and `email`.

        Raises:
        - Unauthorized: If no authorization header is present or the token is invalid.
        - ScopeMissing: If the required 'identify' scope is not present in the token's scope list.
        - HTTPError: If there is an issue with the network or the server response when trying to fetch the user data.
        - Exception: For any other unexpected errors encountered during the execution.
        """

        access_token = await self.check_token(request)

        if 'identify' not in self.scopes:
            raise ScopeMissing('identify')
        
        route = self.api + '/users/@me'
        headers = {'Authorization': 'Bearer ' + access_token}

        return await self.fetch('GET', route, headers, return_class=User)

    async def get_user_by_id(self, user_id: str) -> User:
        """
        Asynchronously retrieves detailed user information by user ID from the authentication server using the bot's access token.

        This method fetches the profile data of a specific user by their unique user ID. It requires a bot token for authentication, which must be pre-configured. This is particularly useful in scenarios where applications need to fetch user data without direct user interaction, relying instead on bot credentials.

        Parameters:
        - user_id (str): The unique identifier for the user whose data is to be retrieved. This is a globally unique identifier that represents an individual user.

        Returns:
        - User: An instance of the User class populated with the detailed profile data of the user. The User class typically includes fields such as `id`, `username`, `avatar`, `discriminator`, and possibly `email` if the bot has the necessary permissions.

        Raises:
        - ValueError: If a bot token has not been set prior to invoking this method.
        - Unauthorized: If the bot token is invalid or expired.
        - HTTPError: If there is an issue with the network or the server response when trying to fetch the user data.
        - Exception: For any other unexpected errors encountered during the execution.
        """

        if not self.bot_token:
            raise ValueError('Bot token is required')

        route = self.api + f'/users/{user_id}'
        headers = {'Authorization': 'Bot ' + self.bot_token}

        return await self.fetch('GET', route, headers, return_class=User)

    async def get_user_guilds(self, request: Request) -> list[Guild]:
        """
        Asynchronously retrieves a list of guilds (servers) the user is part of from the authentication server using a valid access token.

        This method first validates the presence of an 'Authorization' header in the provided request, extracts the access token, and checks if the required 'guilds' scope is included in the initial authorization request. If the scope is missing, it raises a ScopeMissing exception. If the scope is present, it proceeds to fetch the list of guilds from the endpoint that provides guild information associated with the user.

        Parameters:
        - request (Request): The request object from which the access token will be extracted. This object must contain an 'Authorization' header with a bearer token.

        Returns:
        - list[Guild]: A list of Guild objects, each containing details about a guild such as its ID, name, icon, permissions, and whether the user is an owner. This list provides a comprehensive view of the user's guild memberships.

        Raises:
        - Unauthorized: If no authorization header is present, or the token is invalid.
        - ScopeMissing: If the required 'guilds' scope is not present in the token's scope list.
        - HTTPError: If there is an issue with the network or the server response when trying to fetch the guild data.
        - Exception: For any other unexpected errors encountered during the execution.
        """

        access_token = await self.check_token(request)

        if 'guilds' not in self.scopes:
            raise ScopeMissing('guilds')
        
        route = self.api + '/users/@me/guilds'
        headers = {'Authorization': 'Bearer ' + access_token}

        return await self.fetch('GET', route, headers, return_class=Guild)

    # apps
    async def get_app(self) -> dict:
        """
        Asynchronously retrieves the application details associated with the bot from the authentication server using a valid bot token.

        This method accesses the '/applications/@me' endpoint to fetch the application details of the bot. It ensures that a bot token is set; if not, it raises a ValueError. This function is useful for bot developers who need to retrieve information such as the application's ID, name, icon, and permissions.

        Returns:
        - dict: A dictionary containing key details about the application. This includes application ID, name, icon, description, and other relevant metadata that describe the bot application.

        Raises:
        - ValueError: If a bot token has not been set prior to invoking this method, indicating that the method cannot proceed without authentication.
        - Unauthorized: If the bot token provided is invalid or expired.
        - HTTPError: If there is an issue with the network or the server response when trying to fetch the application data.
        - Exception: For any other unexpected errors encountered during the execution.
        """

        if self.bot_token is None:
            raise ValueError('Bot token is required')

        route = self.api + '/applications/@me'
        headers = {'Authorization': 'Bot ' + self.bot_token}

        return await self.fetch('GET', route, headers)
