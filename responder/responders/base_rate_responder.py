import random

import discord
from redbot.core.bot import Red

from ..unicornia import strings
from .base_text_responder import BaseTextResponder


class BaseRateResponder(BaseTextResponder):
    enabled: bool = False
    title: str = "[RATE]"
    description: str = "❯ {target} is {rating}%"
    thumbnail: str = None
    footer: str = None

    # this enables hard-coding overrides for specific user ids
    # dictionary should be defined as a [user.id] = {[embed properties:values]}
    user_overrides: dict = {}

    # this enables changing embed properties for rating values
    rating_overrides = {}

    def __init__(self, parent, bot: Red):
        # TextResponderBase is an abstract base class and doesn't have an init
        self.parent = parent
        self.bot = bot

    @staticmethod
    def get_rating():
        """Overwrite this method if you don't want a random number between 0 and 100

        Returns:
            int: Rating as an int
        """
        return random.randint(0, 100)

    def get_property(self, property: str, target: discord.Member, rating: int):
        """Retrieve a property value for a given target member and rating.

        1. This method first checks if the target member has any user-specific overrides.
        If an override exists for the given property, it returns that value.
        2. If no user-specific override is found, it checks for rating-specific overrides
        in descending order of rating. If a rating-specific override is found, it returns
        that value.
        3. If no overrides are found, it returns the default property value.

        Args:
            property (str): The name of the property to retrieve.
            target (discord.Member): The target member for whom the property is being retrieved.
            rating (int): The rating value to check for rating-specific overrides.

        Returns:
            Any: The value of the requested property, either from user-specific overrides,
             rating-specific overrides, or the default property value.
        """

        if target.id in self.user_overrides:
            value = self.user_overrides.get(target.id).get(
                property, getattr(self, property)
            )
            return random.choice(value) if isinstance(value, list) else value

        for key in sorted(self.rating_overrides.keys(), reverse=True):
            if rating >= key:
                value = self.rating_overrides[key].get(
                    property, getattr(self, property)
                )
                return random.choice(value) if isinstance(value, list) else value

        return getattr(self, property)

    def get_title(self, target: discord.Member, rating: int):
        return self.get_property("title", target, rating)

    def get_description(self, target: discord.Member, rating: int):
        return self.get_property("description", target, rating)

    def get_footer(self, target: discord.Member, rating: int):
        return self.get_property("footer", target, rating)

    def get_thumbnail(self, target: discord.Member, rating: int):
        thumbnail = self.get_property("thumbnail", target, rating)
        if not thumbnail:
            thumbnail = target.display_avatar.url

        return thumbnail

    async def respond(self, message: discord.Message, target: discord.Member = None):
        rating = self.get_rating()
        title = self.get_title(target, rating)
        description = self.get_description(target, rating)
        footer = self.get_footer(target, rating)
        thumbnail = self.get_thumbnail(target, rating)

        description = strings.format_string(
            description, target=target.display_name, rating=rating
        )

        await self.send_embed(
            message,
            title=title,
            description=description,
            thumbnail=thumbnail,
            footer=footer,
        )
