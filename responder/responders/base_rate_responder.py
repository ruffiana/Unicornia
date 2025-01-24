"""Abstract base class for rate responders.

Rate responders are used to generate a rating for a given target member.
The most basic form of these is a very simple call/response that will 
create an embed with a title, description, and thumbnail.

The title, description, and thumbnail can be customized by overwriting
the class properties, or they can be customized on a per-user basis by
overwriting the `user_overrides` dictionary.

Embed properties:
    title: str = "[RATE]"
    description: str = "❯ {target} is {rating}%"
    thumbnail: str = "https://example.com/default_thumbnail.png"
    footer: str = None

The rating can be a random number between 0 and 100, or it can be
customized by overwriting the .get_rating() method. Note that the rating
is used to determine which rating-specific overrides to use. See Below.

User-specific overrides can be defined in the `user_overrides` dictionary.
This dictionary should be defined as a [user.id] = {[embed properties:values]}.
If a value is a list, a random choice will be made. This is handy for things like
multiple descriptions or images.

Rating-specific overrides can be defined in the `rating_overrides` dictionary.
This dictionary should be defined as a [rating] = {[embed properties:values]}.
Keys are sorted in descending order, and the first key that is less than or equal
to the rating will be used.
Like the user-specific overrides, if a value is a list, a random choice
will be made.
Note: user-specific overrides take precedence over rating-specific overrides.

Finally, the 'respond' method can be overwritten to extend the behavior
defined by the base class, or to completely replace with custom behavior.
In all cases, this method is required for the responder to function.
"""

import random

import re

import discord
from redbot.core.bot import Red

from ..unicornia import strings
from .base_text_responder import BaseTextResponder


class BaseRateResponder(BaseTextResponder):
    enabled: bool = False

    title: str = "[RATE]"
    description: str = "❯ {target} is {rating}%"
    thumbnail: str = None  # "https://example.com/default_thumbnail.png"
    footer: str = None

    # this enables hard-coding overrides for specific user ids
    # dictionary should be defined as a [user.id] = {[embed properties:values]}
    # if a value is a list, a random choice will be made. This is handy for things like
    # multiple descriptions or images.
    user_overrides: dict = {}

    # this enables changing embed properties for rating values
    rating_overrides = {}

    def __init__(self, parent, bot: Red):
        # BaseTextResponder is an abstract class which does not have an
        # init, so don't call super().__init__ here.
        self.parent = parent
        self.bot = bot

        self._topic: str = None

    @property
    def topic(self):
        return self._topic

    @topic.setter
    def topic(self, value):
        self._topic = value

    @staticmethod
    def get_rating():
        """Overwrite this method if you don't want a random number between 0 and 100

        Returns:
            int: Rating as an int
        """
        return random.randint(0, 100)

    def get_property(self, property: str, member: discord.Member, rating: int):
        """Retrieve a property value for a given target member and rating.

        1. This method first checks if the target member has any user-specific overrides.
        If an override exists for the given property, it returns that value.
        2. If no user-specific override is found, it checks for rating-specific overrides
        in descending order of rating. If a rating-specific override is found, it returns
        that value.
        3. If no overrides are found, it returns the default property value.

        Args:
            property (str): The name of the property to retrieve.
            member (discord.Member): The target member for whom the property is being retrieved.
            rating (int): The rating value to check for rating-specific overrides.

        Returns:
            Any: The value of the requested property, either from user-specific overrides,
             rating-specific overrides, or the default property value.
        """

        if member.id in self.user_overrides:
            value = self.user_overrides.get(member.id).get(
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

    def get_title(self, member: discord.Member, rating: int):
        return self.get_property("title", member, rating)

    def get_description(self, member: discord.Member, rating: int):
        return self.get_property("description", member, rating)

    def get_footer(self, member: discord.Member, rating: int):
        return self.get_property("footer", member, rating)

    def get_thumbnail(self, member: discord.Member, rating: int):
        thumbnail = self.get_property("thumbnail", member, rating)
        if not thumbnail:
            thumbnail = member.display_avatar.url

        return thumbnail

    async def respond(
        self,
        message: discord.Message,
        target: discord.Member,
        match: re.Match,
    ):
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
