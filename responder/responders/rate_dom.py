import discord
import re

from redbot.core.bot import Red

from ..unicornia import strings
from .base_rate_responder import BaseRateResponder


class DomRate(BaseRateResponder):
    # default title, description, and thumnail is for unknown or 0% rating
    title = "❯ Mysterious..."
    description = "{target} is 1000% mysterious..."
    thumbnail = r"https://cdn.discordapp.com/emojis/828672418318778398.gif"
    footer = "Results scientifically calculated based on member roles."

    user_overrides = {
        # junny
        89582933735665664: {
            "title": "❯ Dominant",
            "description": "❯ {target} is 666% Dominant.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/695147901407592499.webp?size=128&quality=lossless",
        },
        # kirin
        140186220255903746: {
            "title": "❯ Submissive",
            "description": "❯ {target} is 690% Submissive.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/729249758715183144.webp?size=128&quality=lossless",
        },
        # Maid ice:3
        819276102325239840: {
            "title": "❯ Submissive",
            "description": "❯ {target} is 869% Submissive.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/729249758715183144.webp?size=128&quality=lossless",
        },
        # berry
        1058458210060751039: {
            "title": "❯ Submissive",
            "description": "❯ {target} is 555% Submissive.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/729249758715183144.webp?size=128&quality=lossless",
        },
        # ruffiana
        474075064069783552: {
            "title": "❯ Submissive Fuck Toy",
            "description": "❯ {target} is 100% fuck toy.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/816087120526442506.webp?size=128&quality=lossless&animated=true",
        },
    }

    SUB_ROLES = {
        1329908302187855972: 1.00,
        686097362107498504: 1.00,
        768103786119823380: 0.75,
        768103783498121296: 0.75,
        694788843207131246: 1.00,
        694788849020305451: 0.75,
        694788851155337236: 0.20,
        694788853419999352: 0.20,
        694788854942531607: 0.50,
        1074675006006644736: 0.05,
        696082750775492688: 0.20,
        694790765460848701: 1.00,
        696048918248554627: 1.00,
        708022873058574396: 0.25,
        686098506834116620: 0.05,
        686098381214711837: 1.00,
    }

    DOM_ROLES = {
        1329908395578495068: 1.00,
        686097057190379537: 1.00,
        686097106083119115: 1.00,
        694788857371033640: 1.00,
        694788859015462923: 0.25,
        694788860760031243: 0.25,
        694789801353805862: 0.25,
        694789803153162290: 0.25,
        694790101095546890: 0.25,
        694790104044142612: 1.00,
        694790108230189087: 0.25,
        686098541831127048: 0.10,
        811471307106942996: 0.50,
    }

    dominant_properties = {
        "title": "❯ Dominant",
        "description": "{target} is {rating}% Dominant.",
        "thumbnail": r"https://cdn.discordapp.com/emojis/695147901407592499.webp?size=128&quality=lossless",
    }
    submissive_properties = {
        "title": "❯ Submissive",
        "description": "{target} is {rating}% Submissive.",
        "thumbnail": r"https://cdn.discordapp.com/emojis/729249758715183144.webp?size=128&quality=lossless",
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)

    def get_rating(self, member: discord.Member):
        # dom_total = sum(DOM_ROLES.values())
        # sub_total = sum(SUB_ROLES.values())

        dom_rating = sum(
            value
            for role, value in self.DOM_ROLES.items()
            if role in [r.id for r in member.roles]
        )
        sub_rating = sum(
            value
            for role, value in self.SUB_ROLES.items()
            if role in [r.id for r in member.roles]
        )
        rating = dom_rating - sub_rating

        return rating

    def get_property(self, property: str, target: discord.Member, rating: int):
        """Extends the base class method to include dominant/submissive properties."""

        if target.id in self.user_overrides:
            value = self.user_overrides.get(target.id).get(
                property, getattr(self, property)
            )
            return value

        for key in sorted(self.rating_overrides.keys(), reverse=True):
            if rating >= key:
                value = self.rating_overrides[key].get(
                    property, getattr(self, property)
                )
                return value

        # get the property from dominant or submissive if rating if it exists
        if rating > 0.0:
            return self.dominant_properties.get(property, getattr(self, property))
        elif rating < 0.0:
            return self.submissive_properties.get(property, getattr(self, property))

        return getattr(self, property)

    async def respond(
        self, message: discord.Message, target: discord.Member, match: re.Match
    ):
        """Extends the base class method to handle dominant/submissive ratings."""
        rating = self.get_rating(target)
        title = self.get_title(target, rating)
        description = self.get_description(target, rating)
        footer = self.get_footer(target, rating)
        thumbnail = self.get_thumbnail(target, rating)

        # convert rating ratio to positive percentage for display#
        rating = rating * 100 if rating > 0.0 else rating * -100
        rating = round(rating)

        description = strings.format_string(
            description, target=target.display_name, rating=rating
        )

        await self.send_embed(
            message,
            title=title,
            description=description,
            thumbnail=thumbnail,
            footer=footer,
            delay=True,
        )
