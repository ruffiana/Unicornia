"""Main module for roleplay bot"""

import asyncio
import logging
from random import choice
from typing import List

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.predicates import MessagePredicate

from . import __version__, const
from .actions import ACTIONS
from .help import Help
from .settings import Settings


class Roleplay(commands.Cog):
    def __init__(self, bot: commands.Bot = Red):
        # super().__init__(self, bot)

        self.bot = bot

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.helper = Help(bot=bot, parent=self)
        self.user_settings = Settings(bot=bot, parent=self, helper=self.helper)

        self.create_action_commands()

    @commands.group(invoke_without_command=True)
    async def roleplay(self, ctx: commands.Context):
        """Parent command for roleplay settings."""
        if ctx.invoked_subcommand is None:
            return await self.helper.roleplay(ctx)

    @roleplay.command(aliases=["help"])
    async def roleplay_help(self, ctx: commands.Context):
        """Subcommand for roleplay help"""
        self.logger.debug("Default help for `roleplay` command intercepted.")
        return await self.helper.roleplay(ctx)

    @roleplay.group(invoke_without_command=True)
    async def settings(self, ctx: commands.Context, member: discord.Member = None):
        """Parent command for roleplay settings."""
        if ctx.invoked_subcommand is None:
            return await self.user_settings.manage_settings(ctx, member=member)

    @settings.command(aliases=["help"])
    async def settings_help(self, ctx: commands.Context):
        self.logger.debug("Default help for `roleplay settings` command intercepted.")
        return await self.helper.settings(ctx)

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """Sets up listener to override default help menu for cog

        Args:
            ctx (commands.Context): The context of the command invocation.
            error (commands.CommandError): CommandError passed in as arg
        """
        self.logger.debug("Command Error: {error}")
        if isinstance(error, commands.CommandNotFound) and ctx.command is None:
            # don't send the roleplay help otherwise it will spam for
            # every & command
            # await self.roleplay_help.roleplay(ctx)
            pass

    def create_action_commands(self):
        """Factory to create command methods roleplay action"""
        for action, details in ACTIONS.items():
            help = details.get("help", f"{action}s a member.")
            aliases = details.get("aliases", [])

            self.create_action_command(action, help, aliases)

    def create_action_command(
        self, action: str, help_text: str, aliases: List[str]
    ) -> None:
        """Creates a new command for a roleplay action

        Args:
            action (str): The name of the command.
            help_text (str): The help text for the command.
            aliases (List[str]): A list of aliases for the command.

        Returns:
            None
        """

        # method needs to be defined here so it can be changed for each action
        async def command_method(
            ctx: commands.Context, *, member: discord.Member = None
        ):
            """Executes the specified action for the given member.

            Args:
                ctx (commands.Context): The context of the command invocation.
                member (Optional, discord.Member): The member to perform the action on.

            Returns:
                None
            """
            await self.do_action(ctx, action, target_member=member)

        command_method.__name__ = action
        command_method.__doc__ = help_text

        # include capitalized version of command and aliases
        aliases.extend([a.capitalize() for a in aliases])
        aliases.append(action.capitalize())

        command = commands.command(name=action, aliases=aliases)(command_method)
        command = commands.cooldown(
            const.COOLDOWN_RATE, const.COOLDOWN_TIME, commands.BucketType.channel
        )(command)
        command = commands.bot_has_permissions(embed_links=True)(command)

        setattr(self, action, command)
        # self.__cog_commands__ = getattr(self, '__cog_commands__', tuple()) + (command,)
        self.bot.add_command(command)

    async def do_action(
        self, ctx: commands.Context, action: str, target_member: discord.Member = None
    ):
        """Wrapper method that handles consent and assembling messages"""
        # if a member doesn't specific a target user or uses the command on themselves,
        if target_member is None:
            target_member = ctx.author

        # if target member and author are the same, change the author so that the
        # default user/bot performs it instead
        if target_member.id == ctx.author.id:
            default_member = self.user_settings.users_manager.get_default_user_id(ctx)
            self.logger.debug(
                f"Action performed by member on themselves. Substituting {default_member}."
            )
            author = ctx.message.guild.get_member(default_member)
        else:
            author = ctx.author

        # If the member calling the command is in the target member's blocked list, or
        # vice-versa send message that the command can't be used
        blocked_by_target = await self.user_settings.users_manager.in_group(
            target_member, author, "blocked"
        )
        target_blocked = await self.user_settings.users_manager.in_group(
            author, target_member, "blocked"
        )
        if blocked_by_target or target_blocked:
            return await ctx.send(
                f"{author.mention}, you can't use that command on {target_member.display_name}."
            )

        # If the member has one of the roles that automatically denies the command, send
        # the denial message. Examples might be "Locked" or "Honorary Chastity"
        # TODO: This may need more refinement between when a member is calling a command
        # vs when a command is used on them
        roles = ACTIONS[action].get("deny_roles", [])
        self.logger.debug(f"Auto denial role IDs: {roles}")
        for role_id in roles:
            if await self.user_settings.users_manager.has_role(
                ctx, target_member, role_id
            ):
                self.logger.debug(
                    f"Role ID:{role_id} in member roles. Action will be auto-denied"
                )
                deny_message = ACTIONS[action].get("deny_message", const.DENY_MESSAGE)
                return await ctx.send(
                    deny_message.format(
                        author=author.mention, target=target_member.mention
                    )
                )

        # If the member has the public use setting, execute the command
        public = await self.user_settings.config.user(target_member).public()
        self.logger.debug(f"{target_member.display_name} public flag: {public}")
        if public:
            return await self.send_action_message(ctx, author, target_member, action)

        # If the author calling the command is in the target's owner list, execute the command
        is_owner = await self.user_settings.users_manager.in_group(
            target_member, author, "owners"
        )
        if is_owner:
            return await self.send_action_message(ctx, author, target_member, action)

        # If the author calling the command is in the target's allowed list, execute the command
        is_allowed = await self.user_settings.users_manager.in_group(
            target_member, author, "allowed"
        )
        if is_allowed:
            return await self.send_action_message(ctx, author, target_member, action)

        # if the target has the 'selective user' flag, then decline the command
        # this needs to happen after checks for owners and allowed users so we
        # can just assume every one else is neither at this point forward
        selective = await self.user_settings.config.user(target_member).selective()
        self.logger.debug(f"{target_member.display_name} selective flag: {selective}")
        if selective:
            return await ctx.send(
                const.REFUSAL_MESSAGE.format(target=target_member.display_name)
            )

        # Check to see if the command requires consent
        consent_required = ACTIONS[action].get("consent_required", False)
        self.logger.debug(f"{action} consent required: {consent_required}")

        if not consent_required:
            return await self.send_action_message(ctx, author, target_member, action)

        # get the consent message and wait for target member or their owner to respond
        owners = await self.user_settings.users_manager.list_users(
            ctx, target_member, "owners"
        )
        """
        TODO: For now, just using the first owner in the users list. I'm not sure what
        we want to do if there multiples. Which owner should we ask for permission?
        All of them? First? Try to figure out who's online or active?
        """
        owner = await ctx.guild.fetch_member(owners[0])
        if owner:
            owner = await ctx.guild.fetch_member(owners[0])
            consent_message = ACTIONS[action]["consent_owner"]

            await ctx.send(
                consent_message.format(
                    owner=owner.mention,
                    author=author.mention,
                    target=target_member.mention,
                )
            )
            # use MessagePredicate to wait for a 'yes' or 'no' response from the targeted member's owner
            pred = MessagePredicate.yes_or_no(ctx, ctx.channel, owner)
        else:
            consent_message = ACTIONS[action]["consent_message"]

            await ctx.send(
                consent_message.format(
                    author=author.mention, target=target_member.mention
                )
            )
            # use MessagePredicate to wait for a 'yes' or 'no' response from the targeted member
            pred = MessagePredicate.yes_or_no(ctx, ctx.channel, target_member)

        # wait for either the target member or owner to respond
        try:
            await self.bot.wait_for("message", timeout=const.TIMEOUT, check=pred)
        # if the member/owner takes too long to respond, send the timeout message
        except asyncio.TimeoutError:
            if owner:
                return await ctx.send(
                    const.TIMEOUT_MESSAGE.format(user=owner.display_name)
                )
            else:
                return await ctx.send(
                    const.TIMEOUT_MESSAGE.format(user=target_member.display_name)
                )

        # if the member/owner declines consent, send this message
        # TODO: This could also be easily extended to use a custom decline consent
        # message if you wanted to
        if not pred.result:
            # We may not want to send a message if consent is refused
            return await ctx.send(
                const.REFUSAL_MESSAGE.format(target=target_member.display_name)
            )

        return await self.send_action_message(ctx, author, target_member, action)

    async def send_action_message(
        self,
        ctx: commands.Context,
        author: discord.Member,
        member: discord.Member,
        action=str,
    ):
        """Sends the final message or Embed for the roleplay command

        Args:
            ctx (commands.Context): The context of the command invocation.
            author (discord.Member): The user who invoked the command.
            member (discord.Member): The member to perform the action on.
            action (str): Name of the action command invoked.

        Returns:
           None
        """
        # get a random image from the list of images using random.choice()
        # TODO: This could be extended to get an image dynamically or allow for a single
        # URL as a string
        image = choice(ACTIONS[action]["images"])
        # get the action description message
        description = ACTIONS[action]["description"]
        # get footer if it exists and append to default footer
        footer = ACTIONS[action].get("footer")
        footer = f"{const.EMBED_FOOTER} - {footer}" if footer else const.EMBED_FOOTER

        # if the action uses the "spoiler" flag, we can't create an Embed as
        # there's currently no way to spoiler an image in an Embed
        description = description.format(author=author.mention, target=member.mention)
        if ACTIONS[action].get("spoiler"):
            # use pipes to spoiler image
            return await ctx.send(f"{description}\n|| {image} ||")
        else:
            embed = discord.Embed(description=description, color=const.EMBED_COLOR)
            embed.set_image(url=image)
            # don't add member avatar to action embed
            # avatar = await self.settings.users_manager.get_member_avatar(ctx, member)
            # embed.set_thumbnail(url=avatar)
            if footer:
                embed.set_footer(text=footer)
            else:
                embed.set_footer(text=const.EMBED_FOOTER)
            return await ctx.send(embed=embed)

    async def delete_message(self, ctx: commands.Context):
        """Deletes a message by its ID with exception handling for missing permissions

        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        try:
            # Attempt to delete the message
            await ctx.message.delete()
            self.logger.debug(f"Message {ctx.message.id} deleted successfully.")
        except discord.Forbidden:
            # Handle missing permissions
            self.logger.debug(
                f"I don't have permission to delete message {ctx.message.id}"
            )
        except discord.NotFound:
            # Handle message not found
            self.logger.debug(
                f"Message {ctx.message.id} not found. It may have already been deleted."
            )
        except discord.HTTPException as e:
            # Handle other HTTP exceptions
            self.logger.debug(f"Failed to delete message {ctx.message.id}: {e}")

    def reset_cooldown(self, ctx: commands.Context, action: str):
        """Reset the cooldown for the invoking user."""
        command = getattr(self, action)
        bucket = command._buckets.get_bucket(ctx.message)
        bucket.reset()
