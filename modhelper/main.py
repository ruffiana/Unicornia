import logging
import discord
from fuzzywuzzy import process
from redbot.core import commands
from redbot.core.bot import Red
from typing import List, Tuple

from . import __version__, __author__, const


class ModHelper(commands.Cog):
    def __init__(self, bot: commands.Bot = Red):
        self.bot: commands.Bot = bot

        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

    @commands.command()
    async def find(
        self,
        ctx: commands.Context,
        username: str,
        min_score: int = 70,
        max_results: int = const.EMBED_LIST_LIMIT,
    ) -> None:
        """
        Find a user by username using fuzzy matching.

        Args:
            ctx (commands.Context): The command context.
            username (str): The username to search for.
            min_score (int, optional): The minimum score threshold for matching. Defaults to 70.
            max_results (int, optional): The maximum number of results to display. Defaults to const.EMBED_LIST_LIMIT.
        """
        members: List[discord.Member] = ctx.guild.members
        member_names: List[Tuple[str, str]] = [
            (member.display_name, member.name) for member in members
        ]
        search_targets: List[str] = [
            f"{display_name} ({name})" for display_name, name in member_names
        ]

        found_users: List[Tuple[str, int]] = process.extract(
            username, search_targets, limit=max_results
        )
        await self.show_results(ctx, username, found_users, min_score, members)

    async def show_results(
        self,
        ctx: commands.Context,
        username: str,
        found_users: List[Tuple[str, int]],
        min_score: int,
        members: List[discord.Member],
    ) -> None:
        """
        Display the search results.

        Args:
            ctx (commands.Context): The command context.
            username (str): The username searched for.
            found_users (List[Tuple[str, int]]): List of found users with scores.
            min_score (int): The minimum score threshold for matching.
            members (List[discord.Member]): List of guild members.
        """
        results: List[str] = []
        for user, score in found_users:
            # Only include matches that meet the minimum score
            if score < min_score:
                continue

            display_name, name = user.split(" (")
            name = name.rstrip(")")
            member = discord.utils.get(members, name=name)
            if member:
                results.append(
                    f"{member.display_name} ({member.name}) - ID: {member.id}"
                )

        if results:
            await ctx.send("\n".join(results))
        else:
            await ctx.send(
                f"No matches found for '{username}' with the minimum score of {min_score}."
            )
