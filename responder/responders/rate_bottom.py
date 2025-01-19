"""Botom Rate Responder

Responds with a rating % and a gif for how bottom the target is.
"""

from redbot.core.bot import Red

from .base_rate_responder import BaseRateResponder
from .. import const


class BottomRate(BaseRateResponder):
    title = "❯ Bottom Rate"
    description = "{target} is {rating}% bottom"

    bottom = {
        "title": "❯ Bottom!!",
        "description": "❯ {target} is very bottom",
        "thumbnail": r"https://cdn.discordapp.com/emojis/1093690664119717939.webp?size=512&quality=lossless",
    }

    user_overrides = {
        # Kirin
        const.KIRIN_ID: bottom,
        # Butts
        641228870795657256: bottom,
        # Jessi
        117012698964819976: bottom,
        # Ryan
        843188175596945429: bottom,
        # ice
        819276102325239840: bottom,
    }
