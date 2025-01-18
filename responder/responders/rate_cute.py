from redbot.core.bot import Red

from .base_rate_responder import BaseRateResponder
from .. import const


class CuteRate(BaseRateResponder):
    title = "❯ Cute Rate"
    description = "{target} is 100% Cute"

    user_overrides = {
        const.RUFFIANA_ID: {
            "description": [
                "I'm sure {target} has a great...personality...",
                "{target}...?\n\nCute??..No.\n\nSorry, but no.",
                "{target}??\n\nLOL!!",
                "{target} is definitely *not* cute!",
            ]
        }
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)
