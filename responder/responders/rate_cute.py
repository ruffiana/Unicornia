from redbot.core.bot import Red

from .base_rate_responder import BaseRateResponder


class CuteRate(BaseRateResponder):
    title = "❯ Cute Rate"
    description = "{target} is 100% Cute"

    not_cute_descriptions = [
        "I'm sure {target} has a great...personality...",
        "{target}...?\n\nCute??..No.\n\nSorry, but no.",
        "{target}??\n\nLOL!!",
        "{target} is definitely *not* cute!",
    ]

    user_overrides = {
        # ruffiana
        474075064069783552: {"description": not_cute_descriptions}
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)
