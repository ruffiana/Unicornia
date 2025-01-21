""" Rate Anything

This is the default, all-purpose rate responder. It will respond with a
simple rating % and randomly selected gif from Tenor.
"""

import random
import re

import discord
from redbot.core.bot import Red

from ..unicornia import web
from .base_rate_responder import BaseRateResponder


class RateAnything(BaseRateResponder):
    SUPPORTER_ROLE_ID = 700121551483437128

    def get_random_gif(self):
        # Search tenor for an appropriate thumbnail image
        search_term = self.topic.replace(" ", "-")
        gifs = web.get_tenor_gifs(search_term)
        gif_url = random.choice(gifs)

        return gif_url

    def is_approved(self, message: discord.Message):
        if message.author.guild_permissions.administrator:
            return True
        if any(role.id == self.SUPPORTER_ROLE_ID for role in message.author.roles):
            return True
        return False

    async def respond(
        self,
        message: discord.Message,
        target: discord.Member,
        match: re.Match,
    ):
        # Check if the user is an approved user
        if not self.is_approved(message):
            return

        rating = self.get_rating()

        title = " ".join(word.capitalize() for word in self.topic.split())
        title = "❯ {topic} Rate".format(topic=title)

        thumbnail = self.get_random_gif()

        description = "{target} is {rating}% {topic}".format(
            target=target.display_name, rating=rating, topic=self.topic
        )

        footer = r"The rate anything command is only available to supporters."

        await self.send_embed(
            message,
            title=title,
            description=description,
            thumbnail=thumbnail,
            footer=footer,
            delay=False,
        )
