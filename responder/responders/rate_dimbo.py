"""Dimbo Rate Responder

Responds with a random % rating for how 'dimbo' a user is.
"""

from redbot.core.bot import Red

from .base_rate_responder import BaseRateResponder
from .. import const


class DimboRate(BaseRateResponder):
    title = "❯ Dimbo Rate"
    description = "{target} is {rating}% Dimbo"

    # dictionary of properties for the embed so we don't have to copy/paste
    # it a bunch of times
    dimbo_defaults = {
        "title": "ERROR_CODE_4",
        "color": 16711680,
        "description": "User is too DIMBO to calculate.",
    }

    user_overrides = {
        const.RUFFIANA_ID: dimbo_defaults,
        # Emma#8765
        532750893326663681: {
            "description": "❯ {target} is the Dimbo! \nAlso not in charge.",
            "thumbnail": r"https://cdn.discordapp.com/attachments/686096388018405408/765924143279112252/dimbo.png?size=1024&quality=lossless",
        },
        # girldicks (kira)
        614500671147999233: dimbo_defaults,
        # adrii.111  (Adriana)
        1110256621524885586: dimbo_defaults,
        # unknown user
        # 14018622025590374: dimbo_defaults,
        # unknown user
        # 1032686173849653425: dimbo_defaults,
    }

    rating_overrides = {
        90: {
            "title": "❯ Like...Totally Dimbo",
            "thumbnail": r"https://cdn.discordapp.com/attachments/686096388018405408/765924132822319114/dimbo3.png?size=1024&quality=lossless",
        },
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)
