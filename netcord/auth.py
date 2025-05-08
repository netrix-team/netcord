from httpx import Response
from urllib.parse import urlencode

from ._http import HTTPClient
from .models import Oauth2Token, User, Guild
from .errors import AuthenticationError, TokenExchangeError

from .config import (
    DEFAULT_SCOPES, DISCORD_API_BASE_URL,
    API_VERSION, AUTHORIZATION_BASE_URL, TOKEN_URL
)

__all__ = (
    'OauthClient',
)


class OauthClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: tuple[str, ...] = DEFAULT_SCOPES,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        self.scopes = tuple(scopes)
        self._scope_str = ' '.join(self.scopes)

        self.base_api_url = f'{DISCORD_API_BASE_URL}/{API_VERSION}'
        self._http = HTTPClient(base_url=self.base_api_url)

    def generate_auth_url(self, state: str = None, prompt: str = 'consent') -> str:  # noqa: E501
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self._scope_str
        }

        if state:
            params['state'] = state
        if prompt:
            params['prompt'] = prompt

        query = urlencode(params)
        return f'{AUTHORIZATION_BASE_URL}?{query}'

    async def exchange_code(self, code: str) -> Oauth2Token:
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response: Response = await self._http.post(
            TOKEN_URL, data=data, headers=headers
        )

        if response.status_code != 200:
            detail = f'Failed to exchange code: HTTP {response.status_code}'

            try:
                error_data = response.json()
                if 'error' in error_data:
                    detail = f'Failed to exchange code: {error_data['error']}'
            except Exception:
                pass

            raise TokenExchangeError(detail, response.status_code)

        token_data = response.json()
        token = Oauth2Token(**token_data)
        return token

    async def refresh_token(self, refresh_token: str) -> Oauth2Token:
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response: Response = await self._http.post(
            TOKEN_URL, data=data, headers=headers
        )

        if response.status_code != 200:
            detail = f'Failed to refresh token: HTTP {response.status_code}'

            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_desc = (error_data.get('error_description')
                                  or error_data.get('error'))
                    detail = f'Failed to refresh token: {error_desc}'
            except Exception:
                pass

            raise TokenExchangeError(detail, response.status_code)

        token_data = response.json()
        token = Oauth2Token(**token_data)
        return token

    async def fetch_user(self, access_token: str) -> User:
        headers = {'Authorization': f'Bearer {access_token}'}
        response: Response = await self._http.get('/users/@me', headers=headers)  # noqa: E501

        if response.status_code != 200:
            raise AuthenticationError(
                'Failed to fetch user info: Unauthorized',
                response.status_code
            )

        user_data = response.json()
        user = User(**user_data)
        return user

    async def fetch_guilds(self, access_token: str) -> list[Guild]:
        headers = {'Authorization': f'Bearer {access_token}'}
        response: Response = await self._http.get('/users/@me/guilds', headers=headers)  # noqa: E501

        if response.status_code != 200:
            raise AuthenticationError(
                'Failed to fetch user guilds: Unauthorized or Forbidden',
                response.status_code
            )

        guilds_data = response.json()
        guilds = [Guild(**guild) for guild in guilds_data]
        return guilds

    async def close(self) -> None:
        await self._http.close()
