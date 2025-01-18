from redbot.core.bot import Red

from .base_rate_responder import BaseRateResponder


class DimboRate(BaseRateResponder):
    title = "❯ Dimbo Rate"
    description = "{target} is {rating}% Dimbo"

    dimbo_defaults = {
        "title": "ERROR_CODE_4",
        "color": 16711680,
        "description": "User is too DIMBO to calculate.",
    }

    user_overrides = {
        532750893326663681: {  # Emma#8765
            "description": "❯ {target} is the Dimbo! \nAlso not in charge.",
            # "thumbnail": r"https://cdn.discordapp.com/attachments/686096388018405408/765924143279112252/dimbo.png?size=1024&quality=lossless",
        },
        1032686173849653425: dimbo_defaults,
        614500671147999233: dimbo_defaults,
        1110256621524885586: dimbo_defaults,
        14018622025590374: dimbo_defaults,
        474075064069783552: dimbo_defaults,
    }

    rating_overrides = {
        90: {
            "title": "❯ Like...Totally Dimbo",
            # "thumbnail": r"https://cdn.discordapp.com/attachments/686096388018405408/765924132822319114/dimbo3.png?size=1024&quality=lossless",
        },
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)
