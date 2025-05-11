from typing import Optional
from .config import DISCORD_CDN_BASE_URL

from pydantic import BaseModel, Field
from pydantic import field_validator, ConfigDict

__all__ = (
    'Oauth2Token',
    'User',
    'Guild',
)


class Oauth2Token(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)
    expires_in: int = Field(...)
    scope: Optional[str] = Field(None)
    refresh_token: Optional[str] = Field(None)

    model_config = ConfigDict(extra='ignore')

    def to_dict(self, **kwargs) -> dict:
        return self.model_dump(mode='json', **kwargs)

    @property
    def bearer(self) -> str:
        return f'Bearer {self.access_token}'


class User(BaseModel):
    id: str = Field(...)
    username: str = Field(...)
    discriminator: str = Field(...)
    avatar: Optional[str] = Field(None)
    avatar_url: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    bot: Optional[bool] = Field(False)
    mfa_enabled: Optional[bool] = Field(False)
    banner: Optional[str] = Field(None)
    accent_color: Optional[int] = Field(None)
    locale: Optional[str] = Field(None)
    verified: Optional[bool] = Field(False)

    model_config = ConfigDict(extra='ignore')

    def to_dict(self, **kwargs) -> dict:
        return self.model_dump(mode='json', **kwargs)

    @field_validator('avatar_url', mode='after')
    @classmethod
    def compute_avatar_url(
        cls,
        _: Optional[str],
        values: dict[str, str]
    ) -> Optional[str]:

        user_id = values.get('id')
        avatar_hash = values.get('avatar')
        disc = values.get('discriminator')

        if avatar_hash is None:
            default_idx = 0
            if disc and disc.isdigit():
                default_idx = int(disc) % 5
            elif disc is None and user_id:
                default_idx = int(user_id) % 5
            return f'{DISCORD_CDN_BASE_URL}/embed/avatars/{default_idx}.png'

        else:
            ext = 'gif' if avatar_hash.startswith('a_') else 'png'
            return f'{DISCORD_CDN_BASE_URL}/avatars/{user_id}/{avatar_hash}.{ext}?size=1024'  # noqa: E501


class Guild(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    icon: Optional[str] = Field(None)
    icon_url: Optional[str] = Field(None)
    banner: Optional[str] = Field(None)
    banner_url: Optional[str] = Field(None)
    owner: Optional[bool] = Field(None)
    permissions: Optional[str] = Field(None)
    features: Optional[list[str]] = Field(None)

    model_config = ConfigDict(extra='ignore')

    def to_dict(self, **kwargs) -> dict:
        return self.model_dump(mode='json', **kwargs)

    @field_validator('icon_url', mode='after')
    @classmethod
    def compute_icon_url(
        cls,
        _: Optional[str],
        values: dict[str, str]
    ) -> Optional[str]:

        guild_id = values.get('id')
        icon_hash = values.get('icon')

        if icon_hash is None:
            return None

        ext = 'gif' if icon_hash.startswith('a_') else 'png'
        return f'{DISCORD_CDN_BASE_URL}/icons/{guild_id}/{icon_hash}.{ext}?size=1024'  # noqa: E501

    @field_validator('banner_url', mode='after')
    @classmethod
    def compute_banner_url(
        cls,
        _: Optional[str],
        values: dict[str, str]
    ) -> Optional[str]:

        guild_id = values.get('id')
        banner_hash = values.get('banner')

        if banner_hash is None:
            return None

        ext = 'gif' if banner_hash.startswith('a_') else 'png'
        return f'{DISCORD_CDN_BASE_URL}/banners/{guild_id}/{banner_hash}.{ext}?size=1024'  # noqa: E501
