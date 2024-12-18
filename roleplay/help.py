import logging

import discord
from redbot.core import commands

from . import __version__, const
from .actions import ActionManager
from .settings import USER_SETTINGS


class UsersGroup(commands.Group):
    """Mixin class - overwrites defaults to create custom help menus"""

    async def invoke_without_command(self, ctx: commands.Context):
        # Custom behavior when no subcommand is invoked
        await ctx.send("You can use 'Add' or 'Remove' to manage users in this group.")

    async def send_help(self, ctx: commands.Context, command: commands.Command = None):
        await ctx.send(
            "Custom help: Use 'Add' to add a user and 'Remove' to remove a user."
        )

    async def send_help_for(
        self, ctx: commands.Context, command: commands.Command = None
    ):
        # Overriding this to prevent default help messages
        await self.send_help(ctx)


class Help:
    def __init__(self, bot=None, parent=None, action_manager=ActionManager()):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.bot = bot
        self.parent = parent
        self.action_manager = action_manager

    @property
    def bot_avatar_url(self):
        """Fetch and display the bot's avatar URL."""
        return (
            self.bot.user.avatar.url
            if self.bot.user.avatar
            else self.bot.user.default_avatar.url
        )

    async def roleplay(self, ctx: commands.Context):
        """Sends a custom help message for the cog via `roleplay help`

        Doing this because the dynamically added action commands aren't showing up in
        the default help menu for the cog

        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        prefix = await ctx.bot.get_valid_prefixes(ctx.guild)
        prefix = (
            prefix[0] if prefix else "!"
        )  # Use the first valid prefix or default to "!"

        embed = discord.Embed(
            title="Roleplay Commands",
            description="Here are the available commands for the Roleplay cog:",
            color=const.EMBED_COLOR,
        )
        embed.set_thumbnail(url=self.bot_avatar_url)
        embed.set_footer(text=const.EMBED_FOOTER)

        # Subcommands field
        subcommands = f"- **{prefix}roleplay settings**: Show and manage your settings for Roleplay.\nUse `&roleplay settings help` for more detailed help on managing your settings."
        embed.add_field(name="Settings", value=subcommands, inline=False)

        # Actions field
        actions = ""
        # using list method so we can be sure names are sorted alphabetically
        action_names = self.action_manager.list()
        for name in action_names:
            action = self.action_manager.get(name)
            actions += f"- **{prefix}{name}**: {action.help}\n"

        embed.add_field(name="Actions", value=actions, inline=False)

        await ctx.send(embed=embed, delete_after=const.LONG_DELETE_TIME)

    async def settings(self, ctx: commands.Context):
        """Sends a custom help message for the cog via `roleplay settings help`

        Doing this because the dynamically added action commands aren't showing up in
        the default help menu for the cog

        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        prefix = await ctx.bot.get_valid_prefixes(ctx.guild)
        prefix = (
            prefix[0] if prefix else "!"
        )  # Use the first valid prefix or default to "!"

        description = f"""
        Here are the available subcommands for the `{prefix}roleplay settings` command.

        *(**user** can be any of these formats)*:
        - **Username** - Identifies users uniquely across Discord.\n- **ID** - Unique numerical identifier for users, servers, etc.\n- **Mention** - Directly notify and alert a user within a message.
        """
        embed = discord.Embed(
            title="Roleplay Settings", description=description, color=const.EMBED_COLOR
        )
        embed.set_thumbnail(url=self.bot_avatar_url)
        embed.set_footer(text=const.EMBED_FOOTER)

        # Subcommands fields
        for property, settings in USER_SETTINGS.items():
            default = settings.get("default")
            emoji = settings.get("emoji")
            label = settings.get("label")
            desc = settings.get("description")

            if isinstance(default, list):
                embed.add_field(
                    name=f"{emoji} {label}",
                    value=f"- **{prefix}roleplay settings {property}** [`add`|`remove`] **user**\n{desc}\n",
                    inline=False,
                )
            elif isinstance(default, bool):
                embed.add_field(
                    name=f"{emoji} {label}",
                    value=f"- **{prefix}roleplay settings {property}** [`True`|`False`]\n{desc}\n",
                    inline=False,
                )

        await ctx.send(embed=embed, delete_after=const.LONG_DELETE_TIME)
