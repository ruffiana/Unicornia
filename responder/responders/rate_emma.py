from redbot.core.bot import Red

from .base_rate_responder import BaseRateResponder


class EmmaRate(BaseRateResponder):
    title = "❯ Emma Rate"
    description: str = "❯ {target} is {rating}% Emma"

    user_overrides: dict = {
        # Emma#8765
        532750893326663681: {
            "description": "❯ {target} is an Emma! Also, not in charge.",
            # this image is no longer valid
            # "thumbnail": r"https://cdn.discordapp.com/avatars/500690884028006420/6bded3f7b343bb8dbec99268f9b84801.png?size=1024",
        },
        # Emma#6688
        240942922285973506: {
            "description": "❯ {target} is *the* Emma!",
        },
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)
