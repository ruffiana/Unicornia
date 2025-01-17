from redbot.core.bot import Red

from .base_rate_responder import BaseRateResponder


class StinkyRate(BaseRateResponder):
    title = "❯ Stinky Rate"
    description = "{target} is {rating}% stinky"
    thumbnail = r"https://cdn.discordapp.com/emojis/1318168707423408138.webp?size=96&quality=lossless"

    user_overrides = {
        # kirin
        819276102325239840: {
            "title": "❯ The Stinkiest",
            "description": "❯ Ice is the stinkiest.",
            "thumbnail": "https://cdn.discordapp.com/emojis/1318168707423408138.webp?size=96&quality=lossless",
        },
        843188175596945429: {
            "title": "❯ Super Stinky",
            "description": "❯ Ryan is super duper stinky.",
            "thumbnail": "https://cdn.discordapp.com/emojis/1318168707423408138.webp?size=96&quality=lossless",
        },
    }

    rating_overrides = {
        90: {"title": "❯ Super Stinky"},
        75: {"title": "❯ Very Stinky"},
        50: {"title": "❯ Stinky"},
        25: {"title": "❯ Kinda Stinky"},
        10: {"title": "❯ Not Stinky"},
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)
