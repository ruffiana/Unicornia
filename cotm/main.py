"""This module defines the `ContestCog` class

ContestCog is a Redbot cog for managing and posting information about
the Cutie of the Month Contest.
The cog includes methods for importing text from files, creating Discord
embeds, retrieving contest channels, formatting text with contest-specific
details, and posting contest information to a designated channel.
"""

from pathlib import Path
import logging

import discord

from redbot.core import commands
from redbot.core.bot import Red

from . import __version__, const
from .unicornia import strings


class ContestCog(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self._contest_number: int = 1

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

    @property
    def contest_number(self) -> str:
        return strings.add_ordinal_suffix(self._contest_number)

    @contest_number.setter
    def contest_number(self, number: int):
        self._contest_number = number

    def _import_txt(self, filename: Path):
        """Imports text from a specified file.

        Args:
            filename (Path): The path to the file to be imported.

        Returns:
            str: The content of the file as a string. Returns an empty string if the file is not found or an error occurs.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                text = file.read()
            self.logger.debug(f"{filename=} loaded successfully.")
            return text
        except FileNotFoundError:
            self.logger.warning(f"{filename=} not found. Starting with empty data.")
        except Exception as e:
            self.logger.error(f"An error occurred while loading {filename=}: {e}")
        return ""

    def _create_embed(
        self,
        title: str,
        description: str,
    ) -> discord.Embed:
        """Creates a Discord embed with the given title and description.

        Args:
            title (str): The title of the embed.
            description (str): The description of the embed.

        Returns:
            discord.Embed: The created embed with the specified title, description, footer, and color.
        """
        embed = discord.Embed(title=title, description=description)

        footer_text = strings.format_string(
            const.FOOTER_TEXT, contest_number=self.contest_number
        )
        embed.set_footer(text=footer_text, icon_url=const.FOOTER_ICON_URL)
        embed.color = const.UNICORNIA_BOT_COLOR

        return embed

    def _get_channel(self, ctx: commands.Context) -> discord.TextChannel:
        """Retrieves the contest information channel for the given context.

        Args:
            ctx (commands.Context): The context from which to retrieve the channel.

        Returns:
            discord.TextChannel: The contest information channel if found, otherwise None.
        """
        channel_id = const.CONTEST_CHANNEL_IDS[ctx.guild.id]["info"]
        if channel_id is None:
            self.logger.error(
                f"Unable to find contest channel id for Guild ID:{ctx.guild.id}"
            )
            return None

        channel = ctx.guild.get_channel(channel_id)
        if not channel:
            self.logger.error(f"Channel with ID {const.CONTEST_CHANNEL_ID} not found.")
            return

        return channel

    def _format_text(self, ctx: commands.Context, text: str) -> str:
        """
        Formats the given text with contest-specific details.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            text (str): The text to be formatted.

        Returns:
            str: The formatted text with contest details.
        """
        return strings.format_string(
            text,
            contest_number=self.contest_number,
            cutie_role=const.CUTIE_ROLE_MENTION,
            entries_channel=const.ENTRIES_CHANNEL_MENTION,
            winners_channel=const.WINNERS_CHANNEL_MENTION,
        )

    async def _post_contest_info(
        self, ctx: commands.Context, contest_number: int = None
    ):
        """Posts information about the Cutie of the Month Contest to the designated channel.

        This method sends a series of embedded messages to a specific channel, detailing
        the contest description, terms and conditions, prizes, and voting instructions.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            contest_number (int, optional): The contest number to be posted. Defaults to None.
        """
        channel = self._get_channel(ctx)
        if channel is None:
            return await ctx.send(f"Unable to find contest channel on this server!")

        # this updates property as an integer, and gets it a a string with ordinal suffix
        # ex: "52nd", "53rd", etc
        if contest_number is not None:
            self.contest_number = contest_number

        self.contest_number = contest_number

        # post embed for general description of Cutie of the Month Contest
        contest_Embed = self._create_embed(
            const.CONTEST_TITLE,
            self._format_text(ctx, self._import_txt(const.CONTEST_DESCRIPTION)),
        )
        await channel.send(embed=contest_Embed)

        # post embed outlining terms and conditions for the contest
        terms_Embed = self._create_embed(
            const.TERMS_TITLE,
            self._format_text(ctx, self._import_txt(const.TERMS_DESCRIPTION)),
        )
        await channel.send(embed=terms_Embed)

        # post embed listing prizes for the contest
        prizes_Embed = self._create_embed(
            const.PRIZES_TITLE,
            self._format_text(ctx, self._import_txt(const.PRIZES_DESCRIPTION)),
        )
        await channel.send(embed=prizes_Embed)

        # post instructions for how to vote
        votes_Embed = self._create_embed(
            const.VOTES_TITLE,
            self._format_text(ctx, self._import_txt(const.VOTES_DESCRIPTION)),
        )
        await channel.send(embed=votes_Embed)

    @commands.command(aliases=["cotm"])
    @commands.admin_or_permissions(administrator=True)
    async def contest(self, ctx: commands.Context, contest_number: int = None):
        """Handles the contest command.

        Parameters:
            ctx (commands.Context): The context in which the command was invoked.
            contest_number (int, optional): The number of the contest to retrieve information for. Defaults to None.
        """
        await self._post_contest_info(ctx, self._contest_number)
