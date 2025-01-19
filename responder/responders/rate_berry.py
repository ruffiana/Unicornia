""" Berry Rate Responder

This responder will choose a berry type based on the user ID and respond
with a description of the berry and a thumbnail image.
"""

from typing import Any
import re

import discord
from redbot.core.bot import Red

from .. import const
from .base_rate_responder import BaseRateResponder
from ..unicornia import strings


class BerryRate(BaseRateResponder):
    title = "❯ Berry Rate"

    berry_types = {
        "strawberry": {
            "title": "❯ Strawberry",
            "description": "{target} is a sweet, red fruit with a juicy texture.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Garden_strawberry_%28Fragaria_%C3%97_ananassa%29_single2.jpg/800px-Garden_strawberry_%28Fragaria_%C3%97_ananassa%29_single2.jpg?20220126170106",
        },
        "blueberry": {
            "title": "❯ Blueberry",
            "description": "{target} is a small, round, blue fruit that is often used in desserts.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Afin%C4%83.jpg/450px-Afin%C4%83.jpg?20230815131650",
        },
        "raspberry": {
            "title": "❯ Raspberry",
            "description": "{target} is a red or black fruit with a tart flavor and a bumpy texture.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Raspberry_-_whole_%28Rubus_idaeus%29.jpg/800px-Raspberry_-_whole_%28Rubus_idaeus%29.jpg?20201209125004",
        },
        "blackberry": {
            "title": "❯ Blackberry",
            "description": "{target} is a dark purple or black fruit with a sweet and tart flavor.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Blackberry_%28Rubus_fruticosus%29.jpg/800px-Blackberry_%28Rubus_fruticosus%29.jpg?20210222123148",
        },
        "cranberry": {
            "title": "❯ Cranberry",
            "description": "{target} is a small, red fruit with a tart flavor, often used in sauces and juices.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Cranberry_whole.JPG/800px-Cranberry_whole.JPG?20121224121656",
        },
        "gooseberry": {
            "title": "❯ Gooseberry",
            "description": "{target} is a small, round fruit that can be green, red, or purple, with a tart flavor.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Gooseberries.JPG/800px-Gooseberries.JPG?20080722134215",
        },
        "elderberry": {
            "title": "❯ Elderberry",
            "description": "{target} is a small, dark purple fruit that is often used in syrups and jams.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Sambucus-berries.jpg/640px-Sambucus-berries.jpg",
        },
        "mulberry": {
            "title": "❯ Mulberry",
            "description": "{target} is a dark purple or black fruit with a sweet flavor, often used in pies and jams.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Black_mulberry_fruit_%28Morus_nigra%29.jpg/640px-Black_mulberry_fruit_%28Morus_nigra%29.jpg",
        },
        "boysenberry": {
            "title": "❯ Boysenberry",
            "description": "{target} is a large, dark purple fruit with a sweet-tart flavor, a cross between a raspberry and a blackberry.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/MG_9472.jpg/640px-MG_9472.jpg",
        },
        "huckleberry": {
            "title": "❯ Huckleberry",
            "description": "{target} is a small, round, dark blue or black fruit with a sweet-tart flavor, similar to a blueberry.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Single_Huckleberry_with_Stem_Attached.png/640px-Single_Huckleberry_with_Stem_Attached.png",
        },
    }

    user_overrides: dict = {
        # Berry
        1058458210060751039: berry_types["strawberry"],
        # Jun
        89582933735665664: {
            "title": "❯ Juneberry",
            "description": "{target} is a small, dark purple or red fruit possessing a mild sweetness strongly accented by the almond-like flavour of the seeds.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Amelanchier_ovalis3.JPG/540px-Amelanchier_ovalis3.JPG",
        },
    }

    def get_property(
        self, property: str, target: discord.Member, berry_name: str
    ) -> Any:
        """Overwrites base class method

        Uses the berry name to get the property from the berry_types dictionary.

        Args:
            property (str): The property to get.
            target (discord.Member): The target member.
            berry_name (str): The name of the berry.

        Returns:
            Any: The value of the property.
        """

        if target.id in self.user_overrides:
            value = self.user_overrides.get(target.id).get(
                property, getattr(self, property)
            )
            return value
        else:
            berry_properties = self.berry_types.get(berry_name)
            value = berry_properties.get(property)

        if value:
            return value
        else:
            return getattr(self, property)

    def get_berry_type_by_user_id(self, user_id: int):
        """Get a berry type based on the user ID.

        Args:
            user_id (int): The user ID.

        Returns:
            str: The name of the berry type.
        """
        berry_list = list(self.berry_types.keys())
        berry_index = user_id % len(berry_list)
        berry_name = berry_list[berry_index]

        return berry_name

    async def respond(
        self,
        message: discord.Message,
        target: discord.Member,
        match: re.Match,
    ):
        """Extends the base class method to handle dominant/submissive ratings."""
        # instead of a random rating, we're going to get a berry type using the user ID
        berry_name = self.get_berry_type_by_user_id(target.id)

        # get the properties for the embed based
        title = self.get_property("title", target, berry_name)
        description = self.get_property("description", target, berry_name)
        thumbnail = self.get_property("thumbnail", target, berry_name)
        footer = self.get_property("footer", target, berry_name)

        description = strings.format_string(description, target=target.display_name)

        await self.send_embed(
            message,
            title=title,
            description=description,
            thumbnail=thumbnail,
            footer=footer,
            delay=False,
        )
