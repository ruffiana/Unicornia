""" Rate Anything

This is the default, all-purpose rate responder. It will respond with a
simple rating % and randomly selected gif from Tenor.
"""

import random

import discord
from redbot.core.bot import Red

from ..unicornia import web
from .base_rate_responder import BaseRateResponder


class RateAnything(BaseRateResponder):
    def __init__(self, parent, bot: Red, target: discord.Member, topic: str):
        super().__init__(parent, bot)

        self.topic = topic
        self.target = target

        self.rating = self.get_rating()

        self.topic_title = " ".join(word.capitalize() for word in self.topic.split())
        self.title = "❯ {topic} Rate".format(topic=self.topic_title)
        self.thumbnail = self.get_random_gif()
        self.description = "{target} is {rating}% {topic}".format(
            target=self.target.display_name, rating=self.rating, topic=self.topic
        )
        self.footer = r"The rate anything command is only available to supporters."

    def get_random_gif(self):
        # Search tenor for an appropriate thumbnail image
        search_term = self.topic.replace(" ", "-")
        gifs = web.get_tenor_gifs(search_term)
        gif_url = random.choice(gifs)

        return gif_url
