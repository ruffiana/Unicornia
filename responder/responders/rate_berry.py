""" Berry Rate Responder

This responder will choose a berry type based on the user ID and respond
with a description of the berry and a thumbnail image.
"""

import re

import discord
from redbot.core.bot import Red

from .. import const
from .base_rate_responder import BaseRateResponder


class BerryRate(BaseRateResponder):
    title = "❯ Berry Rate"

    berry_types = [
        {
            "title": "strawberry",
            "description": "{target} is a sweet, red fruit with a juicy texture.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Garden_strawberry_%28Fragaria_%C3%97_ananassa%29_single2.jpg/800px-Garden_strawberry_%28Fragaria_%C3%97_ananassa%29_single2.jpg?20220126170106",
        },
        {
            "title": "blueberry",
            "description": "{target} is a small, round, blue fruit that is often used in desserts.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Afin%C4%83.jpg/450px-Afin%C4%83.jpg?20230815131650",
        },
        {
            "title": "raspberry",
            "description": "{target} is a red or black fruit with a tart flavor and a bumpy texture.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Raspberry_-_whole_%28Rubus_idaeus%29.jpg/800px-Raspberry_-_whole_%28Rubus_idaeus%29.jpg?20201209125004",
        },
        {
            "title": "blackberry",
            "description": "{target} is a dark purple or black fruit with a sweet and tart flavor.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Blackberry_%28Rubus_fruticosus%29.jpg/800px-Blackberry_%28Rubus_fruticosus%29.jpg?20210222123148",
        },
        {
            "title": "cranberry",
            "description": "{target} is a small, red fruit with a tart flavor, often used in sauces and juices.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Cranberry_whole.JPG/800px-Cranberry_whole.JPG?20121224121656",
        },
        {
            "title": "gooseberry",
            "description": "{target} is a small, round fruit that can be green, red, or purple, with a tart flavor.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Gooseberries.JPG/800px-Gooseberries.JPG?20080722134215",
        },
        {
            "title": "elderberry",
            "description": "{target} is a small, dark purple fruit that is often used in syrups and jams.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Sambucus-berries.jpg/640px-Sambucus-berries.jpg",
        },
        {
            "title": "mulberry",
            "description": "{target} is a dark purple or black fruit with a sweet flavor, often used in pies and jams.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Black_mulberry_fruit_%28Morus_nigra%29.jpg/640px-Black_mulberry_fruit_%28Morus_nigra%29.jpg",
        },
        {
            "title": "boysenberry",
            "description": "{target} is a large, dark purple fruit with a sweet-tart flavor, a cross between a raspberry and a blackberry.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/MG_9472.jpg/640px-MG_9472.jpg",
        },
        {
            "title": "huckleberry",
            "description": "{target} is a small, round, dark blue or black fruit with a sweet-tart flavor, similar to a blueberry.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Single_Huckleberry_with_Stem_Attached.png/640px-Single_Huckleberry_with_Stem_Attached.png",
        },
    ]

    user_overrides: dict = {        
        # Berry 
        1058458210060751039: berry_types[0],
        # Jun
        89582933735665664: {
            "title": "juneberry",
            "decription": "{target} is a small, dark purple or red fruit possessing a mild sweetness strongly accented by the almond-like flavour of the seeds.",
            "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Amelanchier_ovalis3.JPG/540px-Amelanchier_ovalis3.JPG",
        },
    }

    def __init__(self, parent, bot: Red):
        super().__init__(parent, bot)
        self.parent = parent
        self.bot = bot
        self.bot = bot

    def get_berry_by_user(self, user_id: int):
        berry_index = user_id % len(self.berry_types)
        berry = self.berry_types[berry_index]

        if user_id in self.user_overrides:
            berry = self.user_overrides.get(user_id)

        return berry

    async def respond(
        self, message: discord.Message, target: discord.Member, match: re.Match
    ):
        """Extends the base class method to handle dominant/submissive ratings."""
        berry_properties = self.get_berry_by_user(target.id)

        title = f"❯ {berry_properties.get("title", self.title).capitalize()}"

        thumbnail = berry_properties.get("thumbnail", target.avatar.url)

        description = berry_properties.get("description", self.description)
        description = description.format(target=target.display_name)

        await self.send_embed(
            message,
            title=title,
            description=description,
            thumbnail=thumbnail,
            footer=self.footer,
            delay=False,
        )
