from .models import Guild
from datetime import datetime, timezone as tz

DISCORD_EPOCH = 1420070400000

__all__ = (
    'snowflake_time',
    'check_user_role',
    'utcnow',
    'parse_ts'
)


def snowflake_time(id: str) -> int:
    # Convert a Discord snowflake ID to a timestamp in milliseconds
    return int(((int(id) >> 22) + DISCORD_EPOCH) / 1000)


def check_user_role(guild: Guild) -> str:
    # Check the role of a user in a guild
    if guild.owner:
        return 'owner'

    permissions = int(guild.permissions)
    is_admin = permissions & 0x8

    if is_admin:
        return 'admin'

    return 'member'


def utcnow() -> int:
    # Get the current timestamp in milliseconds
    return int(datetime.now(tz.utc).timestamp() * 1000)


def parse_ts(timestamp: int) -> datetime:
    # Parse a timestamp in milliseconds to a datetime object
    return datetime.fromtimestamp(timestamp / 1000, tz=tz.utc)
