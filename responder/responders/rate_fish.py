"""Dimbo Rate Responder

Reponds with a random % rating for how 'dimbo' a user is.
"""

from redbot.core.bot import Red

from .base_rate_responder import BaseRateResponder


class FishRate(BaseRateResponder):
    title = "❯ Fish Rate"
    description = "{target} is {rating}% Fish"

    fish = {
        "title": "❯ Fish!!",
        "thumbnail": "https://cdn.discordapp.com/emojis/1087018867055919164.webp?size=1024&quality=lossless",
    }

    user_overrides = {
        # Adriana
        1032686173849653425: fish,
        # adrihadry
        1110256621524885586: fish,
    }
