"""Main module for roleplay bot"""

import asyncio
import logging
from pathlib import Path
from random import choice
from typing import List
from urllib.parse import urlparse

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.predicates import MessagePredicate

from . import __version__, __credits__, const
from .actions import Action, ActionManager
from .help import Help
from .settings import Settings
from .strings import format_string
from .embed import Embed
from . import images
from .predicates import CustomMessagePredicate


class Roleplay(commands.Cog):
    def __init__(self, bot: commands.Bot = Red):
        self.bot = bot

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.action_manager = ActionManager(parent=self)
        self.helper = Help(bot=bot, parent=self, action_manager=self.action_manager)
        self.user_settings = Settings(bot=bot, parent=self, helper=self.helper)

        self.create_action_commands()

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

        # Asynchronously update the action_manager
        # this lets us look for locally cached images after the settings config has
        # initialized and set the cog's data folder
        bot.loop.create_task(self.initialize())

    async def initialize(self):
        await self.bot.wait_until_red_ready()
        # make sure to update user_settings first as that creates a data_path attribute
        # needed for action_manager
        self.user_settings.update()
        self.action_manager.update()

    @commands.group(invoke_without_command=True)
    async def roleplay(self, ctx: commands.Context):
        """Parent command for roleplay settings."""
        if ctx.invoked_subcommand is None:
            return await self.helper.roleplay(ctx)

    @roleplay.group(invoke_without_command=True)
    @commands.admin()
    async def admin(self, ctx: commands.Context):
        """Parent command for roleplay admin settings."""
        if ctx.invoked_subcommand is None:
            return

    @admin.group(aliases=["logger"], invoke_without_command=True)
    async def logger_settings(self, ctx: commands.Context):
        """Logger settings for roleplay."""
        if ctx.invoked_subcommand is None:
            level = self.logger.level
            level_name = logging._levelToName.get(level)
            msg = f'Logger level is currently set to "{level_name}".'
            return await ctx.send(msg)

    @admin.command()
    async def download(self, ctx: commands.Context):
        """Downloads all action images into the cog's data folder"""
        images_path = self.user_settings.data_path / "images"

        actions = self.action_manager.list()
        for action_name in actions:
            action = self.action_manager.get(action_name)
            for image_URL in action.images:
                images.save_image_from_url(
                    image_URL, images_path, action_name, action.spoiler
                )

        await ctx.send(f"Roleplay action images downloaded to: {images_path}")

    @logger_settings.command(aliases=["level", "setlevel"])
    async def logger_set_level(self, ctx: commands.Context, level_name: str = None):
        """Set logger level."""
        try:
            level = getattr(logging, level_name.upper())
        except AttributeError:
            msg = f'{level_name.upper()} is not a valid logger level!\n({", ".join(logging._nameToLevel)})'
            self.logger.debug(msg)
            return await ctx.send(msg)

        self.logger.setLevel(level)
        msg = f'Logger level set to "{level_name}".'
        self.logger.info(msg)
        return await ctx.send(msg)

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
        self.logger.error(f"Command Error: {error}")
        if isinstance(error, commands.CommandNotFound) and ctx.command is None:
            # don't send the roleplay help otherwise it will spam for
            # every & command
            # await self.roleplay_help.roleplay(ctx)
            pass

    def create_action_commands(self):
        """Factory to create command methods roleplay action"""
        for action in self.action_manager.actions:
            self.create_action_command(action.name, action.help, action.aliases)

    def create_action_command(
        self, action_name: str, help_text: str, aliases: List[str]
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
            ctx: commands.Context, *, target_member: discord.Member = None
        ):
            """Executes the specified action for the given member.

            Args:
                ctx (commands.Context): The context of the command invocation.
                target_member (Optional, discord.Member): The member to perform the action on.

            Returns:
                None
            """
            invoker_member = ctx.author

            # if a target_member wasn't supplied, the user is requesting the bot/default
            # member perform the action on themselves
            if not target_member or target_member.id == ctx.author.id:
                default_member = self.user_settings.users_manager.get_default_user_id(
                    ctx
                )
                invoker_member = ctx.message.guild.get_member(default_member)
                target_member = ctx.author

            # attempt an interaction
            result = await self.interaction(
                ctx,
                action_name,
                invoker_member,
                target_member,
                interaction_type=const.InteractionType.ACTIVE,
            )

            # if the interaction wasn't successful, reset the cooldown for this command
            if result is not True:
                self.reset_cooldown(ctx, action_name)

            return result

        command_method.__name__ = action_name
        command_method.__doc__ = help_text

        # include capitalized version of command and aliases
        aliases.extend([a.capitalize() for a in aliases])
        aliases.append(action_name.capitalize())

        command = commands.command(name=action_name, aliases=aliases)(command_method)
        command = commands.cooldown(
            const.COOLDOWN_RATE, const.COOLDOWN_TIME, commands.BucketType.channel
        )(command)
        command = commands.bot_has_permissions(embed_links=True)(command)

        setattr(self, action_name, command)
        self.bot.add_command(command)

    @commands.command(aliases=["askfor", "get", "giveme", "gimme", "request"])
    async def ask(
        self,
        ctx: commands.Context,
        action_name: str,
        target_member: discord.Member = None,
    ):
        """Ask another member to perform an action on you

        This command serves as a wrapper for .interaction(). It allows a member to ask
        another member to perform an action on themselves.

        Args:
            ctx (commands.Context): The context of the command invocation.
            action_name (str): The name of the roleplay action.
            target_member (Optional, discord.Member): The member to perform this action on.
        """
        invoker_member = ctx.author

        # if a target_member wasn't supplied, the user is requesting the bot/default
        # member perform the action on them
        if not target_member or target_member.id == ctx.author.id:
            default_member = self.user_settings.users_manager.get_default_user_id(ctx)
            self.logger.debug(
                f"Action performed by member on themselves. Substituting {default_member}."
            )
            target_member = ctx.message.guild.get_member(default_member)

        return await self.interaction(
            ctx,
            action_name,
            invoker_member,
            target_member,
            interaction_type=const.InteractionType.PASSIVE,
        )

    # overwriting the .ask() command function docstring here as this is what shows up
    # in the default help text display
    ask.__doc__ = "Ask another member to perform an action on you"

    async def interaction(
        self,
        ctx: commands.Context,
        action_name: str,
        invoker_member: discord.Member,
        target_member: discord.Member,
        interaction_type: const.InteractionType = const.InteractionType.ACTIVE,
    ):
        """Attempt to perform an action on another member (or yourself)

        Args:
            ctx (commands.Context): The context of the command invocation.
            action_name (str): The name of the roleplay action.
            invoker_member (discord.Member): The member who initiated the command
            target_member (discord.Member): The member being asked to participate.
            interaction_type (Optional, InteractionType): This flag changes the message tense from active
            to passive

        Order of consent:
            Does the action require consent? If not, execute
            If the target has an owner, ask the owner for consent
            If the target is public use? consent


        Returns:
            bool: Return True if conditions were right for roleplay action to happen.
            False otherwise.
        """
        action = self.action_manager.get(action_name)
        if not action:
            self.logger.error(
                f'{self.__class__.__name__}.interaction() called with invalid action "{action_name}"!'
            )
            return False

        # collection settings for invoker and target member
        target_public = await self.user_settings.config.user(target_member).public()
        target_servant = await self.user_settings.config.user(target_member).servant()
        target_selective = await self.user_settings.config.user(
            target_member
        ).selective()
        is_blocked = await self.check_blocked(ctx, invoker_member, target_member)
        is_denied = await self.check_roles(ctx, invoker_member, target_member, action)
        is_allowed = await self.user_settings.users_manager.in_group(
            target_member, invoker_member, "allowed"
        )
        invoker_owner = await self.user_settings.users_manager.get_owner(
            ctx, invoker_member
        )
        target_owner = await self.user_settings.users_manager.get_owner(
            ctx, target_member
        )

        self.logger.debug(
            f"""Ineraction:
            action_name : {action_name}
            invoker_member : {invoker_member}
            target_member : {target_member}
            interaction_type : {interaction_type.value}
            target_public : {target_public}
            target_servant : {target_servant}
            target_selective : {target_selective}
            is_blocked : {is_blocked}
            is_denied : {is_denied}
            is_allowed : {is_allowed}
            invoker_owner : {invoker_owner}
            target_owner : {target_owner}"""
        )

        # make sure neither member is blocked by the other
        if is_blocked:
            self.reset_cooldown(ctx, action_name)
            return False

        # check auto-deny roles
        if is_denied:
            self.reset_cooldown(ctx, action_name)
            return False

        # If the invoker_member owns the target member
        if invoker_member == target_owner:
            await self.send_action_message(
                ctx,
                invoker_member,
                target_member,
                action,
                interaction_type=interaction_type,
            )
            return True

        # If the invoker_member calling the command is in the target's allowed list, execute the command
        if is_allowed:
            await self.send_action_message(
                ctx,
                invoker_member,
                target_member,
                action,
                interaction_type=interaction_type,
            )
            return True

        # if the target has the 'selective user' flag, then decline the command unless:
        # the invoker is their owner
        # the interaction is active and they are public use
        # the interaction is passive and they are servant
        if (
            target_selective
            and (not invoker_owner)
            and (interaction_type == const.InteractionType.ACTIVE and not target_public)
            and (
                interaction_type == const.InteractionType.PASSIVE and not target_servant
            )
        ):
            msg = format_string(
                const.REFUSAL_MESSAGE, target_member=f"**{target_member.display_name}**"
            )
            await ctx.send(msg)
            self.reset_cooldown(ctx, action_name)
            return False

        # does the the command requires consent?
        if (
            action.consent
            and (
                interaction_type == const.InteractionType.PASSIVE and not target_servant
            )
            or (interaction_type == const.InteractionType.ACTIVE and not target_public)
            or (invoker_owner or target_owner)
        ):
            self.logger.debug(f"{action_name} consent is required")
            has_consent = await self.ask_for_consent(
                ctx,
                invoker_member,
                target_member,
                action,
                interaction_type=interaction_type,
                invoker_owner=invoker_owner,
                target_owner=target_owner,
            )
            if has_consent is not True:
                self.reset_cooldown(ctx, action_name)
                return False

        # if we've reached this point we should be clear to proceed with the interaction
        await self.send_action_message(
            ctx,
            invoker_member,
            target_member,
            action,
            interaction_type=interaction_type,
        )
        return True

    async def send_action_message(
        self,
        ctx: commands.Context,
        invoker_member: discord.Member,
        target_member: discord.Member,
        action=Action,
        interaction_type: const.InteractionType = const.InteractionType.ACTIVE,
    ):
        """Sends the final message or Embed for the roleplay command

        Args:
            ctx (commands.Context): The context of the command invocation.
            invoker_member (discord.Member): The user who invoked the command.
            target_member (discord.Member): The member to perform the action on.
            action (Action): Action object containing properties.
            interaction_type (Optional, InteractionType): This flag changes the message tense from active
            to passive

        Returns:
           None
        """
        description = action.description
        self.logger.debug(f"description : {description}")

        if interaction_type == const.InteractionType.ACTIVE:
            description = format_string(
                description,
                invoker_member=invoker_member.mention,
                target_member=target_member.mention,
            )
        # for passive consent type, the invoker is the one receiving the action, so we
        # need to swap the member args
        elif interaction_type == const.InteractionType.PASSIVE:
            description = format_string(
                description,
                invoker_member=target_member.mention,
                target_member=invoker_member.mention,
            )
        else:
            self.logger.error(f"Interaction type {interaction_type} is not supported!")
            return False

        # create the embed object
        embed = discord.Embed(description=description, color=const.EMBED_COLOR)

        # get action credits if it exists and add to default footer text
        footer = const.EMBED_FOOTER
        if action.credits:
            footer = f'{footer}\ncredits: {", ".join(action.credits)}'
        self.logger.debug(f"footer : {footer}")

        # DON'T ADD MEMBER AVATAR TO EMBED
        # avatar = await self.settings.users_manager.get_member_avatar(ctx, member)
        # embed.set_thumbnail(url=avatar)

        # get a random image from the list of images using random.choice()
        # TODO: This could be extended to get an image dynamically or allow for a single
        # URL as a string
        image = choice(action.images)
        # Check if image_url_or_path is a URL
        parsed_url = urlparse(image)
        if parsed_url.scheme in ("http", "https"):
            self.logger.debug(f"image URL : {image}")
        else:
            self.logger.debug(f"image filepath : {image}")
            file_path = Path(image)

        # EMBEDS WON'T SPOILER IMAGES INSIDE THEM
        # Embed.spoiler_image() creates manages a local cache and uses file attachments
        # which makes for a bit nicer presentation
        embed.set_footer(text=footer, icon_url=self.bot.user.avatar.url)
        if action.spoiler:
            if parsed_url.scheme in ("http", "https"):
                async with ctx.typing():
                    embed, file = Embed.spoiler_image(image, embed)
            else:
                file = discord.File(fp=file_path, filename=file_path.name)
            await ctx.send(description, file=file)
        else:
            if parsed_url.scheme in ("http", "https"):
                embed.set_image(url=image)
                await ctx.send(embed=embed)
            else:
                file = discord.File(fp=file_path, filename=file_path.name)
                embed.set_image(url=f"attachment://{file_path.name}")
                await ctx.send(embed=embed, file=file)

    async def delete_message(
        self, ctx: commands.Context, delay: int = const.SHORT_DELETE_TIME
    ):
        """Deletes a message by its ID with exception handling for missing permissions

        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        # Adding a delay before deleting the message
        await asyncio.sleep(delay)

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

    def reset_cooldown(self, ctx: commands.Context, command_name: str):
        """Reset the cooldown for the invoking user."""
        command = self.bot.get_command(command_name)
        if command is not None:
            bucket = command._buckets.get_bucket(ctx)
            bucket.reset()
            self.logger.debug(f'Reset cooldown on"{command_name}" command.')
        else:
            self.logger.error(f'Invalid command name: "{command_name}".')

    async def check_roles(
        self,
        ctx: commands.Context,
        invoker_member: discord.User,
        target_member: discord.User,
        action: Action,
    ):
        # If the member has one of the roles that automatically denies the command, send
        # the denial message. Examples might be "Locked" or "Honorary Chastity"
        # TODO: This may need more refinement between when a member is calling a command
        # vs when a command is used on them

        # if no roleIDs are defined, there's nothing to check
        if action.denial is None or action.denial.roles is None:
            return False

        # check to see if the target member has any of the denial roles
        # for this action
        self.logger.debug(f"Auto denial role IDs: {action.denial.roles}")
        for role_id in action.denial.roles:
            if await self.user_settings.users_manager.has_role(
                ctx, target_member, role_id
            ):
                self.logger.debug(
                    f"Role ID:{role_id} in member roles. Action will be auto-denied"
                )
                deny_message = action.denial
                deny_message = format_string(
                    deny_message,
                    invoker_member=f"**{invoker_member.display_name}**",
                    target_member=f"**{target_member.display_name}**",
                )
                self.logger.debug(f"deny_message: {deny_message}")
                await ctx.send(deny_message)
                return True

        return False

    async def check_blocked(
        self,
        ctx: commands.Context,
        invoker_member: discord.User,
        target_member: discord.User,
    ):
        # If the member calling the command is in the target member's blocked list, or
        # vice-versa send message that the command can't be used
        target_member_blocked = await self.user_settings.users_manager.in_group(
            invoker_member, target_member, "blocked"
        )
        invoker_member_blocked = await self.user_settings.users_manager.in_group(
            target_member, invoker_member, "blocked"
        )
        is_blocked = invoker_member_blocked or target_member_blocked
        self.logger.debug(
            f"""Checking blocked status:
                invoker_member_blocked : {invoker_member_blocked}
                target_member_blocked : {target_member_blocked}
                is blocked : {is_blocked}"""
        )
        if is_blocked:
            await ctx.send(
                f"**{invoker_member.display_name}**, you can't use that command on **{target_member.display_name}**."
            )
            return True
        return False

    async def ask_for_consent(
        self,
        ctx: commands.Context,
        invoker_member: discord.User,
        target_member: discord.User,
        action: Action,
        interaction_type: const.InteractionType = const.InteractionType.ACTIVE,
        invoker_owner: discord.User = None,
        target_owner: discord.User = None,
    ):
        self.logger.debug(
            f"""get_consent():
            ctx: {ctx}
            \tinvoker_member: {invoker_member}
            \ttarget_member: {target_member}
            \taction: {action.name}
            \tinteraction_type={interaction_type}
            \tinvoker_owner: {invoker_owner}
            \ttarget_owner: {target_owner}
            """
        )

        # special-case handler for when the invoker is an admin, and
        # the target is a bot
        if invoker_member.guild_permissions.administrator and target_member.bot:
            return True

        # collect owners for invoker and target members
        if not invoker_owner:
            invoker_owner = await self.user_settings.users_manager.get_owner(
                ctx, invoker_member
            )
        if not target_owner:
            target_owner = await self.user_settings.users_manager.get_owner(
                ctx, target_member
            )

        # if both invoker and target have owners, ask both for permission
        if invoker_owner and target_owner:
            owners_mention = f"**{invoker_owner.mention}** & **{target_owner.mention}**"
            owners_display_name = (
                f"{invoker_owner.display_name} & {target_owner.display_name}"
            )
            # interaction type is an Enum, so need it's value as string
            consent_message = getattr(
                action.consent, f"owners_{interaction_type.value}"
            )
            consent_message = f"{consent_message} {const.CONSENT_QUESTION}"
            consent_message = format_string(
                consent_message,
                owner=owners_mention,
                invoker_member=f"**{invoker_member.display_name}**",
                target_member=f"**{target_member.display_name}**",
            )
            self.logger.debug(f'consent_message : "{consent_message}"')
            # send the consent message
            await ctx.send(consent_message)

            # wait for response from owner
            pred = CustomMessagePredicate.yes_or_no(
                ctx, ctx.channel, [invoker_owner, target_owner]
            )
            try:
                await self.bot.wait_for("message", timeout=const.TIMEOUT, check=pred)
            except asyncio.TimeoutError:
                await ctx.send(const.TIMEOUT_MESSAGE.format(user=owners_display_name))
                return False

            # if the either owner declines consent, send this message
            if not pred.result:
                refusal_message = const.OWNER_REFUSAL_MESSAGE.format(
                    owner=target_owner.display_name,
                    invoker_member=f"**{invoker_member.display_name}**",
                    target_member=f"**{target_member.display_name}**",
                )
                await ctx.send(refusal_message)
                return False
            else:
                return True
        # if only the invoker has an owner
        elif invoker_owner and invoker_owner != target_member:
            # interaction type is an Enum, so need it's value as string
            consent_message = getattr(action.consent, f"owner_{interaction_type.value}")
            consent_message = f"{consent_message} {const.CONSENT_QUESTION}"
            consent_message = format_string(
                consent_message,
                owner=invoker_owner.mention,
                invoker_member=f"**{invoker_member.display_name}**",
                target_member=f"**{target_member.display_name}**",
            )
            self.logger.debug(f'consent_message : "{consent_message}"')
            await ctx.send(consent_message)

            # wait for response from owner
            pred = CustomMessagePredicate.yes_or_no(ctx, ctx.channel, invoker_owner)
            try:
                await self.bot.wait_for("message", timeout=const.TIMEOUT, check=pred)
            except asyncio.TimeoutError:
                await ctx.send(const.TIMEOUT_MESSAGE.format(user=owner.display_name))
                return False

            # if the owner declines consent, send this message
            if not pred.result:
                refusal_message = const.OWNER_REFUSAL_MESSAGE.format(
                    owner=invoker_owner.display_name,
                    invoker_member=f"**{invoker_member.display_name}**",
                    target_member=f"**{target_member.display_name}**",
                )
                await ctx.send(refusal_message)
                return False

            # don't return True here, as we still need to check the target for consent

        # if only the target has an owner
        elif target_owner:
            # interaction type is an Enum, so need it's value as string
            consent_message = getattr(action.consent, f"owner_{interaction_type.value}")
            consent_message = f"{consent_message} {const.CONSENT_QUESTION}"
            consent_message = format_string(
                consent_message,
                owner=target_owner.mention,
                invoker_member=f"**{invoker_member.display_name}**",
                target_member=f"**{target_member.display_name}**",
            )
            self.logger.debug(f'consent_message : "{consent_message}"')
            await ctx.send(consent_message)

            # wait for response from owner
            pred = CustomMessagePredicate.yes_or_no(ctx, ctx.channel, target_owner)
            try:
                await self.bot.wait_for("message", timeout=const.TIMEOUT, check=pred)
            except asyncio.TimeoutError:
                await ctx.send(const.TIMEOUT_MESSAGE.format(user=owner.display_name))
                return False

            # if the owner declines consent, send this message
            if not pred.result:
                refusal_message = const.OWNER_REFUSAL_MESSAGE.format(
                    owner=target_owner.display_name,
                    invoker_member=f"**{invoker_member.display_name}**",
                    target_member=f"**{target_member.display_name}**",
                )
                await ctx.send(refusal_message)
                return False
            # we can return True here as the owner has given consent
            else:
                return True

        # Otherwise, no owners are involved and we ask the target member for consent
        # interaction type is an Enum, so need it's value as string
        consent_message = getattr(action.consent, interaction_type.value)
        consent_message = f"{consent_message} {const.CONSENT_QUESTION}"
        consent_message = format_string(
            consent_message,
            invoker_member=f"**{invoker_member.display_name}**",
            target_member=target_member.mention,
        )
        self.logger.debug(f'consent_message : "{consent_message}"')
        await ctx.send(consent_message)

        # wait for response from target member
        pred = CustomMessagePredicate.yes_or_no(ctx, ctx.channel, target_member)
        try:
            await self.bot.wait_for("message", timeout=const.TIMEOUT, check=pred)
        except asyncio.TimeoutError:
            await ctx.send(
                const.TIMEOUT_MESSAGE.format(user=f"**{target_member.display_name}**")
            )
            return False

        if not pred.result:
            refusal_message = const.REFUSAL_MESSAGE.format(
                target_member=f"**{target_member.display_name}**"
            )
            await ctx.send(refusal_message)
            return False
        else:
            return True
