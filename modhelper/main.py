"""
ModHelper Cog

This module contains the ModHelper class, which provides commands to assist with
moderation tasks in a Discord server.

Commands:
    Find: The find command uses fuzzy matching to search for users by their username
    or display name.
"""

import logging
import re
from typing import List, Tuple
from operator import itemgetter

import discord
from rapidfuzz import process, fuzz
from redbot.core import commands
from redbot.core.bot import Red

from . import __author__, __version__
from dataclasses import dataclass


@dataclass
class Member:
    name: str
    display_name: str
    id: int
    score: int = 0


class ModHelperCog(commands.Cog):
    def __init__(self, bot: commands.Bot = Red):
        self.bot: commands.Bot = bot

        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )
        self.logger.setLevel(logging.INFO)

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

    def get_members(self, ctx: commands.Context) -> List[Member]:
        members = []
        for member in ctx.guild.members:
            members.append(
                Member(id=member.id, name=member.name, display_name=member.display_name)
            )
        return members

    @commands.command()
    async def find(
        self,
        ctx: commands.Context,
        *username: str,
        score: int = 85,
        limit: int = 5,
    ) -> None:
        """
        Find a user by username using fuzzy matching.

        Args:
            ctx (commands.Context): The command context.
            username (str): The username to search for.
            score (int, optional): The minimum score threshold for matching. Defaults to 85.
            limit (int, optional): The maximum number of results to display. Defaults to 5.

        Returns:
            None
        """
        username = " ".join(username)
        matched_members = self.search_members(ctx, username, score_threshold=score)
        await self.show_results(ctx, username, matched_members[:limit])

    def search_members(self, ctx, search_term, score_threshold=85):
        members = self.get_members(ctx)
        # Create a list of tuples (id, name) for both name and display_name
        names = [member.name for member in members]
        display_names = [member.display_name for member in members]

        # Use rapidfuzz to get the best matches
        results_names = process.extract(
            search_term,
            names,
            scorer=fuzz.ratio,
            score_cutoff=score_threshold,
            limit=len(names),
        )
        results_display_names = process.extract(
            search_term,
            display_names,
            scorer=fuzz.ratio,
            score_cutoff=score_threshold,
            limit=len(display_names),
        )

        # Combine results from names and display_names
        # Sort combined results by score in descending order
        combined_results = results_names + results_display_names
        combined_results.sort(key=itemgetter(1), reverse=True)

        # Create a set to track added member ids to avoid duplicates
        added_member_ids = set()

        # Create a list to store the ordered Member objects
        matched_members = []

        for result in combined_results:
            member_name, score, index = result
            for member in members:
                if (
                    member.name == member_name or member.display_name == member_name
                ) and member.id not in added_member_ids:
                    member.score = score
                    matched_members.append(member)
                    added_member_ids.add(member.id)

        return matched_members

    async def show_results(
        self,
        ctx: commands.Context,
        username: str,
        matched_members: List[dict],
        limit=5,
    ) -> None:
        """
        Display the search results.

        Args:
            ctx (commands.Context): The command context.
            username (str): The username searched for.
            found_users (List[Tuple[str, int, int]]): List of found users with scores.
            score (int): The minimum score threshold for matching.
            members (List[discord.Member]): List of guild members.
        """
        async with ctx.typing():
            if len(matched_members) == 0:
                msg = f"No matches found for '{username}'."
            elif len(matched_members) < limit:
                msg = f"Found {len(matched_members)} matches for '{username}':"
            else:
                msg = f"Displaying the top {limit} matches for {username}:"

            await ctx.send(msg)

            for member in matched_members:
                # send userID on separate line so it's easier to copy on mobile devices
                await ctx.send(
                    f"### {member.display_name} ({member.name}) - {member.score}%"
                )
                await ctx.send(f"{member.id}")
