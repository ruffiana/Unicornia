import re
from typing import Union

from discord import Guild, Member, NotFound, User
from discord.ext.commands import Context

# this regex pattern is used to match a Discord user mention or user ID
# it will match both <@1234567890> and 1234567890
DISCORD_USER_ID_PATTERN = re.compile(r"<@!?(\d{17,19})>|(\d{17,19})")


async def _get_member_from_user_id(guild: Guild, user_id: int) -> Member:
    """Retrieve a discord.Member object from a Guild using their user ID.

    Args:
        guild (discord.Guild): The guild to search in.
        user_id (int): The user ID of the member to retrieve.

    Returns:
        discord.Member: The member object if found, otherwise None.
    """
    # try to get member from guild cache first, then fetch from API
    discord_member = guild.get_member(user_id)
    if discord_member:
        return discord_member

    try:
        return await guild.fetch_member(user_id)
    except NotFound:
        return None


async def _get_member_from_string(guild: Guild, key: str) -> Member:
    """Retrieve a discord.Member object from a Guild using a string key

    Key can be a mention, discord.User ID, username, or display name

    Args:
        guild (discord.Guild): The guild to search in.
        key (str): The string key to search for (mention or username).

    Returns:
        discord.Member: The member object if found, otherwise None.
    """
    # Does the key match a mention or user ID pattern?
    user_id_match = DISCORD_USER_ID_PATTERN.match(key)
    member_id = user_id_match.group(1) or user_id_match.group(2)
    if user_id_match:
        member_id = int(member_id)
        return await _get_member_from_user_id(guild, member_id)

    # Try to get member by display name
    for member in guild.members:
        if member.display_name == key:
            return member

    # Try to get member by username
    for member in guild.members:
        if str(member) == key or f"{member.name}#{member.discriminator}" == key:
            return member

    return None


async def get_member(ctx: Context, key: Union[str, int, User]) -> Member:
    """Retrieve a discord.Member object from the Context's Guild using a key

    Supported keys:
        string - mention, Discord user ID, username, or display name
        integer - discord.User ID
        discord.User object.

    Args:
        ctx (Context): The command context.
        key (Union[str, int, discord.User]): The key to search for
        (mention, username, user ID, or User object).

    Returns:
        discord.Member: The member object if found, otherwise None.
    """
    # if the key is a User object, try to get the member from the guild
    if isinstance(key, User):
        return await _get_member_from_user_id(ctx.guild, key.id)
    # if the key is an integer, try to get member by user ID
    elif isinstance(key, int):
        return await _get_member_from_user_id(ctx.guild, key)
    # if the key is a string, try to get member by mention or username
    elif isinstance(key, str):
        return await _get_member_from_string(ctx.guild, key)
    else:
        raise ValueError(f'Unsupported key type! "{key}" ({type(key)})')


async def _get_user_from_user_id(ctx: Context, user_id: int) -> Member:
    """Retrieve a user using their Discord user ID.

    Args:
        ctx (Context): The command context.
        user_id (int): The user ID of the user to retrieve.

    Returns:
        discord.User: The User object if found, otherwise None.
    """
    # try and get from cache first, then fetch from API
    discord_user = ctx.bot.get_user(user_id)
    if discord_user:
        return discord_user

    try:
        return await ctx.bot.fetch_user(user_id)
    except NotFound:
        return None


async def _get_user_from_string(ctx: Context, key: str) -> Member:
    """Retrieve a user using a string key

    Args:
        ctx (Context): The command context.
        key (str): The string key to search for (mention or username).

    Returns:
        discord.User: The User object if found, otherwise None.
    """
    # does the key match a user mention or user ID?
    user_id_match = DISCORD_USER_ID_PATTERN.match(user_id)
    if user_id_match:
        user_id = int(user_id_match.group(1))
        return await _get_user_from_user_id(user_id)

    # Try to get user by username or name#discriminator
    for discord_user in ctx.bot.users:
        if (
            str(discord_user) == key
            or f"{discord_user.name}#{discord_user.discriminator}" == key
        ):
            return discord_user

    return None


async def get_user(ctx: Context, key: Union[str, User]) -> User:
    """Retrieve a discord.User object from the Context using a key

    Supported keys:
        string - mention, Discord user ID, username, or display name
        integer - discord.User ID
        discord.Member object.

    Args:
        ctx (Context): The command context.
        key (Union[str, Member]): The key to search for (mention, username, user ID, or Member object).

    Returns:
        discord.User: The User object if found, otherwise None.
    """
    if isinstance(key, Member):
        return await _get_user_from_user_id(ctx, key.id)
    elif isinstance(key, int):
        return await _get_user_from_user_id(ctx, key)
    elif isinstance(key, str):
        return await _get_user_from_string(ctx, key)
    else:
        raise ValueError(f'Unsupported key type! "{key}" ({type(key)})')
