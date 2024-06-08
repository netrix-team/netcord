import random
from typing import Optional

from pydantic import BaseModel, Field
from pydantic import Extra, model_validator

DISCORD_CDN = 'https://cdn.discordapp.com'


class Token(BaseModel):
    token_type: str
    expires_in: int
    scope: str | list[str]

    access_token: str
    refresh_token: str


class User(BaseModel):
    id: str
    username: str

    bot: Optional[bool] = False
    email: Optional[str] = None

    avatar_url: str = None
    avatar_hash: str = Field(alias='avatar', default=None)

    locale: Optional[str] = None
    verified: Optional[bool] = None
    mfa_enabled: Optional[bool] = None

    @model_validator(mode='after')
    def get_user_avatar_url(self):
        if self.avatar_hash:
            self.avatar_url = self.user_avatar_url(
                user_id=self.id, avatar_hash=self.avatar_hash)
        else:
            self.avatar_url = self.default_avatar_url()

    def user_avatar_url(self, user_id: str, avatar_hash: str) -> str:
        extension = '.gif' if avatar_hash.startswith('a_') else '.png'
        return f'{DISCORD_CDN}/avatars/{user_id}/{avatar_hash}{extension}'

    @staticmethod
    def default_avatar_url() -> str:
        number = random.randint(0, 5)
        return f'{DISCORD_CDN}/embed/avatars/{number}.png'

    class Config:
        extra = Extra.ignore


class Guild(BaseModel):
    id: str
    name: str
    owner: bool

    icon_url: Optional[str] = None
    icon_hash: Optional[str] = Field(alias='icon', default=None)

    @model_validator(mode='after')
    def get_guild_icon_url(self):
        if self.icon_hash:
            self.icon_url = self.guild_icon_url(
                guild_id=self.id, icon_hash=self.icon_hash)
        else:
            self.icon_url = None  # Нужно будет заменить на что-то

    def guild_icon_url(self, guild_id: str, icon_hash: str) -> str:
        extension = '.gif' if icon_hash.startswith('a_') else '.png'
        return f'{DISCORD_CDN}/icons/{guild_id}/{icon_hash}{extension}'

    class Config:
        extra = Extra.ignore
