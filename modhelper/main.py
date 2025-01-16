"""
ModHelper Cog

This module contains the ModHelper class, which provides commands to assist with
moderation tasks in a Discord server.

Commands:
    Find: The find command uses fuzzy matching to search for users by their username
    or display name.
"""

import logging
from typing import List, Tuple

import discord
from fuzzywuzzy import process
from redbot.core import commands
from redbot.core.bot import Red

from . import __author__, __version__, const


class ModHelperCog(commands.Cog):
    def __init__(self, bot: commands.Bot = Red):
        self.bot: commands.Bot = bot

        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

    def normalize_string(self, s: str) -> str:
        return s.strip().lower()

    @commands.command()
    async def find(
        self,
        ctx: commands.Context,
        *username: str,
        score: int = 85,
        results: int = 5,
    ) -> None:
        """
        Find a user by username using fuzzy matching.

        Args:
            ctx (commands.Context): The command context.
            username (str): The username to search for.
            score (int, optional): The minimum score threshold for matching. Defaults to 85.
            results (int, optional): The maximum number of results to display. Defaults to 5.
        """
        username = " ".join(username)
        members: List[discord.Member] = ctx.guild.members
        member_names: List[Tuple[str, str]] = [
            (
                self.normalize_string(member.display_name),
                self.normalize_string(member.name),
            )
            for member in members
        ]
        search_targets: List[str] = [
            f"{display_name} ({name})" for display_name, name in member_names
        ]
        normalized_username = self.normalize_string(username)

        found_users: List[Tuple[str, int]] = process.extract(
            normalized_username, search_targets, limit=results
        )

        if not found_users:
            return await ctx.send(f"No good matches found for '{username}'.")

        await self.show_results(ctx, username, found_users, score, members)

    async def show_results(
        self,
        ctx: commands.Context,
        username: str,
        found_users: List[Tuple[str, int]],
        score: int,
        members: List[discord.Member],
    ) -> None:
        """
        Display the search results.

        Args:
            ctx (commands.Context): The command context.
            username (str): The username searched for.
            found_users (List[Tuple[str, int]]): List of found users with scores.
            score (int): The minimum score threshold for matching.
            members (List[discord.Member]): List of guild members.
        """
        for user, match_score in found_users:
            # Only include matches that meet the minimum score
            if match_score < score:
                continue

            _, name = user.split(" (")
            name = name.rstrip(")")
            member = discord.utils.get(members, name=name)

            if not member:
                continue

            # send userID on separate line so it's easier to copy on mobile devices
            await ctx.send(f"### {member.display_name} ({member.name})")
            await ctx.send(f"{member.id}")
