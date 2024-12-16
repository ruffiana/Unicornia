"""Users Module

This module provides a class for managing lists of Discord User IDs in a member's config property.
It includes functionalities for adding, removing, and listing users, checking roles, and handling
permissions for actions involving users.

Classes:
    - Manager: Manages lists of Discord User IDs in a member's config property.
"""

import asyncio
from dataclasses import dataclass
import logging
from random import choice
from typing import List, Optional, Union

import discord
from redbot.core import commands
from redbot.core.utils.predicates import MessagePredicate

from . import const
from .strings import get_indefinite_article
from .user_settings import USER_SETTINGS


@dataclass
class Pronouns:
    subject: str  # e.g., "they"
    object: str  # e.g., "them"
    possessive: str  # e.g., "their"


# defined here instead of const to avoid circular import
PRONOUNS_HE = (Pronouns(subject="he", object="him", possessive="his"),)
PRONOUNS_SHE = (Pronouns(subject="she", object="her", possessive="her"),)
PRONOUNS_THEY = (Pronouns(subject="they", object="them", possessive="their"),)
PRONOUN_ROLES = {
    686112295155138580: PRONOUNS_HE,
    686112244609712139: PRONOUNS_SHE,
    686112332459671600: PRONOUNS_THEY,
}


class Manager:
    """
    This class manages lists of Discord User IDs in a member's config property.

    Attributes:
        bot (commands.Bot): The instance of the Redbot bot.
        config (Config): The configuration object for managing settings.

    Methods:
        init_logging(): Sets up logging for the Manager class.
        in_group(member, user_id, users_group): Checks if a user is in the member's config group.
        add_user(ctx, member, users_group, user_id, permission): Adds a user to a member's config.
        remove_user(ctx, member, users_group, user_id): Removes a user from a member's config.
        list_users(ctx, member, users_group, as_display, as_string): Lists users in a member's config.
        convert_ids(user_ids, as_string): Converts a list of user IDs to display names.
        has_role(ctx, member, role_id): Checks if a member has a specific role by ID.
    """

    def __init__(self, bot: commands.Bot, config):
        """Subclass to manager user data

        Args:
            bot (commands.Bot): The instance of the Redbot bot.
            config (Config): The configuration object for managing settings.
        """
        self.init_logging()

        self.bot = bot
        self.config = config

    def init_logging(self):
        """Sets up logging for the Manager class."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

    async def in_group(
        self,
        member: discord.Member,
        user_or_id: Union[discord.User, int],
        users_group: str,
    ) -> bool:
        """
        Checks if a user is in the member's config group.

        Args:
            member (discord.Member): Discord member to check.
            user_or_id (Union[discord.Member, int]): Discord member or user ID to be checked.
            users_group (str): Name of the config property for the users group.

        Returns:
            bool: True if user is in the group, False otherwise.
        """
        # Ensure user_or_id is an integer ID
        user_id = (
            user_or_id.id if isinstance(user_or_id, discord.Member) else user_or_id
        )

        async with self.config.user(member).get_attr(users_group)() as user_ids:
            in_group = user_id in user_ids
            self.logger.debug(f"{user_id} in {member} group {users_group}: {in_group}")
            return in_group

    async def add_user(
        self,
        ctx: commands.Context,
        member: discord.Member,
        users_group: str,
        user_id: int,
        permission: Optional[dict] = None,
    ):
        """
        Adds a user to a member's config.

        Args:
            ctx (commands.Context): The context of the command invocation.
            member (discord.Member): Discord member to add user to.
            user_id (int): Discord user ID to be added.
            users_group (str): Name of the config property for the users group.
            permission (Optional[dict]): Dictionary of permission values from member settings.

        Returns:
            None
        """
        target_user = self.bot.get_user(user_id)
        if not target_user:
            await ctx.send(
                f"User with ID {user_id} not found in this guild.",
                delete_after=const.SHORT_DELETE_TIME,
            )
            return

        label = USER_SETTINGS[users_group].get("label", "users list")

        async with self.config.user(member).get_attr(users_group)() as user_ids:
            # members are only allowed to have 1 owner
            if users_group == "owners" and user_ids:
                # reduce user_list down to single/first user id
                if len(user_ids) > 1:
                    user_ids = user_ids[:1]
                return await ctx.send(
                    f"{member.display_name} already has {get_indefinite_article(label)} {label}. {choice(const.INSULTS)}",
                    delete_after=const.SHORT_DELETE_TIME,
                )

            # already in the list
            if user_id in user_ids:
                return await ctx.send(
                    f"{target_user.display_name} is already {get_indefinite_article(label)} {label} for {member.display_name}. {choice(const.INSULTS)}",
                    delete_after=const.SHORT_DELETE_TIME,
                )

            # get permission from the prospective member
            if permission and permission.get("required"):
                permission_ask = permission.get("permission_ask")
                permission_accept = permission.get("permission_accept")
                permission_deny = permission.get("permission_deny")

                await ctx.send(
                    permission_ask.format(
                        target=target_user.mention, author=member.display_name
                    )
                )

                pred = MessagePredicate.yes_or_no(ctx, ctx.channel, target_user)
                try:
                    await self.bot.wait_for(
                        "message", timeout=const.TIMEOUT, check=pred
                    )
                except asyncio.TimeoutError:
                    return await ctx.send(
                        const.TIMEOUT_MESSAGE.format(user=target_user.display_name)
                    )

                if pred.result:
                    user_ids.append(user_id)
                    await ctx.send(
                        permission_accept.format(
                            target=target_user.display_name, author=member.display_name
                        )
                    )
                else:
                    return await ctx.send(
                        permission_deny.format(
                            target=target_user.display_name, author=member.display_name
                        )
                    )
            else:
                user_ids.append(user_id)
                return await ctx.send(
                    f"{target_user.display_name} has been added as {get_indefinite_article(label)} {label} for {member.display_name}.",
                    delete_after=const.SHORT_DELETE_TIME,
                )

    async def add_user_to_group(
        self,
        ctx,
        member: discord.Member,
        user_key: Union[int, str],
        users_group: str,
        exclusion_groups: List[str] = None,
    ):
        """Abstract method to add a user to a member's group list

        Args:
            ctx (commands.Context): The context of the command invocation.
            member (discord.Member): The member whose group list is being managed.
            user_key (Union[int, str]): The ID, username, or mention of the user to be
            added to the group.
            users_group (str): The name of the group to add the user to.
            exclusion_groups (List[str], optional): Groups that the user should not be a
            part of. Defaults to None.

        Returns:
           None
        """
        # make sure the user_id is a valid member
        user = await self.get_user(ctx, user_key)
        if user is None:
            return await ctx.send(
                f"Please use a valid user ID, username, or mention. {choice(const.INSULTS)}.",
                delete_after=const.SHORT_DELETE_TIME,
            )

        label = USER_SETTINGS[users_group].get("label", "users list")
        permission = USER_SETTINGS[users_group].get("permission", None)

        # You can't add yourself
        if user.id == member.id:
            return await ctx.send(
                f"{member.display_name} tried to add themselves as {get_indefinite_article(label)} {label}. {choice(const.INSULTS)}",
                delete_after=const.SHORT_DELETE_TIME,
            )

        # check exclusion groups
        for excluded_group in exclusion_groups:
            in_group = await self.in_group(ctx.author, user.id, excluded_group)
            if in_group:
                excluded_label = USER_SETTINGS[excluded_group].get(
                    "label", "users list"
                )
                return await ctx.send(
                    f"{user.display_name} is {get_indefinite_article(excluded_label)} {excluded_label} for {member.display_name}. They can't be added as {get_indefinite_article(label)} {label}. {choice(const.INSULTS)}!",
                    delete_after=const.SHORT_DELETE_TIME,
                )

        # see if the user group needs permissions and pass dict along to function
        await self.add_user(
            ctx, ctx.author, users_group, user.id, permission=permission
        )

    async def remove_user(
        self,
        ctx: commands.Context,
        member: discord.Member,
        user_id: int,
        users_group: str,
    ):
        """
        Removes a user from a member's config.

        Args:
            ctx (commands.Context): The context of the command invocation.
            member (discord.Member): Discord member to remove user from.
            user_id (int): Discord user ID to be removed.
            users_group (str): Name of the config property for the users group.

        Returns:
            None
        """
        user = self.bot.get_user(user_id)
        if not user:
            await ctx.send(f"User with ID {user_id} not found in this guild.")
            return

        async with self.config.user(member).get_attr(users_group)() as user_ids:
            if user_id not in user_ids:
                await ctx.send(
                    f"{user.display_name} is not in {get_indefinite_article(label)} {label} for {member.display_name}. {choice(const.INSULTS)}",
                    delete_after=const.SHORT_DELETE_TIME,
                )
            else:
                user_ids.remove(user_id)
                label = USER_SETTINGS[users_group].get("label", "users list")
                await ctx.send(
                    f"{user.display_name} has been removed as {get_indefinite_article(label)} {label} for {member.display_name}.",
                    delete_after=const.SHORT_DELETE_TIME,
                )

    async def remove_user_from_group(
        self, ctx, member: discord.Member, user_key: int, users_group: str
    ):
        """Abstract method to remove a user from a member's group list

        Args:
            ctx (commands.Context): The context of the command invocation.
            member (discord.Member): The member whose group list is being managed.
            user_key (Union[int, str]): The ID, username, or mention of the user to be
            added to the group.
            users_group (str): The name of the group to add the user to.

        Returns:
           None
        """
        # make sure the user_id is a valid member
        user = await self.get_user(ctx, user_key)
        if user is None:
            return await ctx.send(
                f"Please use a valid user ID, username, or mention. {choice(const.INSULTS)}",
                delete_after=const.SHORT_DELETE_TIME,
            )

        label = USER_SETTINGS[users_group]["label"]

        # You can't remove yourself
        if user.id == member.id:
            return await ctx.send(
                f"{member.display_name} tried to remove themselves as {get_indefinite_article(label)} {label}. {choice(const.INSULTS)}",
                delete_after=const.SHORT_DELETE_TIME,
            )

        # make sure the user_id isn't already in the group list
        in_group = await self.in_group(ctx.author, user.id, users_group)
        if not in_group:
            return await ctx.send(
                f"{user.display_name} is not {get_indefinite_article(label)} {label} for {member.display_name}. {choice(const.INSULTS)}",
                delete_after=const.SHORT_DELETE_TIME,
            )

        return await self.remove_user(ctx, member, user.id, users_group)

    async def list_users(
        self,
        member: discord.Member,
        users_group: str,
        as_display: bool = False,
        as_string: bool = False,
    ) -> Union[List[int], str]:
        """
        Lists users in a member's config.

        Args:
            ctx (commands.Context): The context of the command invocation.
            member (discord.Member): Discord member to list users for.
            users_group (str): Name of the config property for the users group.
            as_display (bool, optional): Whether to return display names instead of IDs. Defaults to False.
            as_string (bool, optional): Whether to return the result as a newline delimited string. Defaults to False.

        Returns:
            Union[List[int], str]: List of user IDs or display names, or a newline delimited string.
        """
        async with self.config.user(member).get_attr(users_group)() as user_ids:
            if as_display:
                return await self.convert_ids(user_ids, as_string=as_string)
            if not user_ids:
                return []
            else:
                return user_ids

    async def get_user(self, ctx, user_key: Union[int, str]):
        """Gets a user from various types

        Args:
            ctx (commands.Context): The context of the command invocation.
            user_key (Union[int, str]): The ID, username, or mention of the user to be
            added to the group.

        Returns:
           discord.User
        """
        user = None
        if isinstance(user_key, int):
            user = self.bot.get_user(user_key)
        elif isinstance(user_key, str):
            # Check for mention format
            if user_key.startswith("<@") and user_key.endswith(">"):
                user_id = int(user_key[2:-1])
                user = self.bot.get_user(user_id)
            else:
                # get a list of members to search through. If ctx.guild.members is valid
                # then we're in a server channel. Otherwise, we're in a direct message
                # and use .get_all_members() to ge a generator with every discord.Member
                # the Discord client can see
                try:
                    members = ctx.guild.members
                except AttributeError:
                    members = self.bot.get_all_members()
                # Search through list of members for a user using their global username
                # or display name
                for guild_member in members:
                    if (
                        guild_member.name == user_key
                        or guild_member.display_name == user_key
                    ):
                        user = guild_member
                        break

        if user is None:
            self.logger.warning(f'Unable to find user using "{user_key}".')
            return None
        else:
            self.logger.debug(
                f"Found {user.display_name} ({user.id}) using {user_key} as key."
            )
            return user

    async def convert_ids(
        self, user_ids: List[int], as_string: bool = False
    ) -> Union[List[str], str]:
        """
        Convert a list of user IDs to list of display names.

        Args:
            user_ids (List[int]): List of Discord user IDs.
            as_string (bool, optional): If True, return the list of names as a newline delimited string. Defaults to False.

        Returns:
            Union[List[str], str]: List of display names or a newline delimited string.
        """
        if not user_ids:
            return "None"

        display_names = []
        for user_id in user_ids:
            try:
                user = await self.bot.fetch_user(user_id)
                display_names.append(user.display_name)
            except discord.NotFound:
                self.logger.error(f"User with ID {user_id} not found.")
                display_names.append(f"Unknown {user_id}")

        return "\n".join(display_names) if as_string else display_names

    async def has_role(
        self, ctx: commands.Context, member: discord.Member, role_key: Union[int, str]
    ) -> bool:
        """
        Checks if the given member has the given role by ID or name.

        Args:
            ctx (commands.Context): The context of the command invocation.
            member (discord.Member): Discord member to check.
            role_key (Union[int, str]): ID or name of the role to check for.

        Returns:
            bool: True if member has the role, False otherwise.
        """
        role = None
        if isinstance(role_key, int):
            role = discord.utils.get(ctx.guild.roles, id=role_key)
        elif isinstance(role_key, str):
            role = discord.utils.get(ctx.guild.roles, name=role_key)

        if role is None:
            self.logger.warning(
                f"Role '{role_key}' not found. It may not exist on this server."
            )
            return False

        return role in member.roles

    async def get_member_avatar(
        self, ctx: commands.Context, member: discord.Member = None
    ):
        """Fetch and display a member's guild avatar and global Discord avatar

        Args:
            ctx (commands.Context): The context of the command invocation.
            member (discord.Member): The member to perform the action on.

        Returns:
            str : URL for a member's avatar as a string
        """
        # Guild-specific avatar (if available)
        guild_avatar_url = member.display_avatar.url
        self.logger.debug("guild_avatar_url : {guild_avatar_url}")

        # Global Discord avatar
        global_avatar_url = member.avatar.url if member.avatar else None
        self.logger.debug("global_avatar_url : {global_avatar_url}")

        return guild_avatar_url if guild_avatar_url else global_avatar_url

    def get_default_user_id(self, ctx: commands.Context) -> Optional[int]:
        """Retrieve the user ID from the dictionary using the guild ID.

        Args:
            ctx (commands.Context): The context of the command invocation.

        Returns:
            Optional[int]: The user ID if found, else None.
        """
        # Check if the context is from a guild
        if ctx.guild:
            guild_id = ctx.guild.id
            return const.DEFAULT_MEMBER_ID.get(guild_id)
        else:
            return self.bot.user.id

    async def get_owner(
        self, ctx: commands.Context, member: discord.Member
    ) -> discord.Member:
        """
        TODO: For now, just using the first owner in the users list. I'm not sure what
        we want to do if there multiples. Which owner should we ask for permission?
        All of them? First? Try to figure out who's online or active?
        """
        owners = await self.list_users(member, "owners")
        owner = await ctx.guild.fetch_member(owners[0]) if owners else None
        self.logger.debug(
            f"Attempted to get owner from {member}: {owner.display_name if owner else None}"
        )

        return owner

    async def get_pronoun(
        self, ctx: commands.Context, member: discord.Member
    ) -> discord.Member:
        for role_id, pronouns in PRONOUN_ROLES.items():
            if self.has_role(member, role_id):
                return pronouns
            else:
                return PRONOUNS_THEY
