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
        self.logger.setLevel(logging.DEBUG)

        self._contest_number: int = 54

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
        embed = discord.Embed(title=title, description=description)

        footer_text = strings.format_string(
            const.FOOTER_TEXT, contest_number=self.contest_number
        )
        embed.set_footer(text=footer_text, icon_url=const.FOOTER_ICON_URL)

        return embed

    def _get_channel(self, ctx: commands.Context) -> discord.TextChannel:
        channel_id = const.CONTEST_CHANNEL_IDS.get(ctx.guild.id)
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

    async def _post_contest_info(self, ctx: commands.Context, contest_number: int):
        channel = self._get_channel(ctx)
        if channel is None:
            return await ctx.send(f"Unable to find contest channel on this server!")

        # this updates property as an integer, and gets it a a string with ordinal suffix
        # ex: "52nd", "53rd", etc
        self.contest_number = contest_number
        contest_number = self.contest_number

        # post embed for general description of Cutie of the Month Contest
        contest_description = self._import_txt(const.CONTEST_DESCRIPTION)
        contest_Embed = self._create_embed(
            const.CONTEST_TITLE,
            strings.format_string(
                contest_description,
                contest_number=contest_number,
            ),
        )
        await channel.send(embed=contest_Embed)

        # post embed outlining terms and conditions for the contest
        terms_description = self._import_txt(const.TERMS_DESCRIPTION)
        terms_Embed = self._create_embed(
            const.TERMS_TITLE,
            strings.format_string(
                terms_description,
                contest_number=contest_number,
            ),
        )
        await channel.send(embed=terms_Embed)

        # post embed listing prizes for the contest
        prizes_description = self._import_txt(const.PRIZES_DESCRIPTION)
        prizes_Embed = self._create_embed(
            const.PRIZES_TITLE,
            strings.format_string(
                prizes_description,
                contest_number=contest_number,
            ),
        )
        await channel.send(embed=prizes_Embed)

        # post instructions for how to vote
        votes_description = self._import_txt(const.VOTES_DESCRIPTION)
        votes_Embed = self._create_embed(
            const.VOTES_TITLE,
            strings.format_string(
                votes_description,
                contest_number=contest_number,
            ),
        )
        await channel.send(embed=votes_Embed)

    @commands.command()
    @commands.admin_or_permissions(administrator=True)
    async def contest(self, ctx: commands.Context, contest_number: int = None):
        if contest_number is not None:
            self.contest_number = contest_number

        await self._post_contest_info(ctx, self._contest_number)
