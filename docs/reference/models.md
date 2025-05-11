# 📦 Models

Pydantic models for tokens, users, guilds.

## `Oauth2Token`

```python
class Oauth2Token(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)
    expires_in: int = Field(...)
    scope: Optional[str] = Field(None)
    refresh_token: Optional[str] = Field(None)
```

## `User`

```python
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
```

!!! Info
    Auto-computed `avatar_url`
    generates a direct link to the user's avatar

## `Guild`

```python
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
```

!!! Info
    Auto-computed `icon_url`, `banner_url`
    generates a direct link to the guild's icon and banner
