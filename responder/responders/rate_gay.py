"""Gay Rate Responder

Reponds with a random % rating for how gay a user is.
This one uses rating_overrides to change the embed title based on the rating.
"""

from redbot.core.bot import Red

from .base_rate_responder import BaseRateResponder
from .. import const


class GayRate(BaseRateResponder):
    title = "❯ Not Gay"
    description = "{target} is {rating}% Gay"
    thumbnail = r"https://cdn.discordapp.com/emojis/1088555199146242248.webp?size=128&quality=lossless"

    user_overrides: dict = {
        const.KIRIN_ID: {
            "title": "❯ The Gay",
            "description": "❯ {target} is the gay.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/817150384111616011.webp?size=128&quality=lossless",
        },
        # Emma#6688
        240942922285973506: {
            "title": "❯ Super Gay",
            "description": "❯ {target} is Super Duper Gay.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/817150384111616011.webp?size=128&quality=lossless",
        },
        # radon  (Radon)
        144523162044858368: {
            "title": "❯ Super Gay",
            "description": "❯ {target} is 99.999% Gay.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/1088555199146242248.webp?size=128&quality=lossless",
        },
    }

    rating_overrides = {
        90: {"title": "❯ Super Gay"},
        80: {"title": "❯ Extremely Gay"},
        70: {"title": "❯ Very Gay"},
        60: {"title": "❯ Quite Gay"},
        50: {"title": "❯ Definitely Gay"},
        40: {"title": "❯ Fairly Gay"},
        30: {"title": "❯ Pretty Gay"},
        20: {"title": "❯ Somewhat Gay"},
        10: {"title": "❯ Kinda Gay"},
        5: {"title": "❯ Slightly Gay"},
    }
