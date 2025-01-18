import re

import discord
from redbot.core.bot import Red

from . import (
    rate_anything,
    rate_bottom,
    rate_cute,
    rate_dimbo,
    rate_dom,
    rate_emma,
    rate_fish,
    rate_gay,
    rate_stinky,
)
from .base_text_responder import BaseTextResponder

IGNORE_WORDS = [
    "separate",
    "celebrate",
    "operate",
    "generate",
    "integrate",
    "moderate",
    "accelerate",
    "concentrate",
    "collaborate",
    "demonstrate",
    "elaborate",
    "illustrate",
    "incorporate",
    "liberate",
    "migrate",
    "narrate",
    "penetrate",
    "saturate",
]


class RateResponder(BaseTextResponder):
    """Parent class that responds to any trigger containing 'rate'"""

    enabled: bool = True
    # \A: Asserts the position at the start of the string.
    # ([\w\s]+): Captures one or more word characters (letters, digits, and underscores) or spaces as the first word or words.
    # \s+: Matches one or more whitespace characters.
    # rate: Matches the literal string "rate".
    # \s*: Matches zero or more whitespace characters.
    # \Z: Asserts the position at the end of the string.
    patterns: list[str] = [r"\A([\w\s]+)\s+rate\s*\Z"]
    ignore_case: bool = True

    rate_classes = {
        "gay": rate_gay.GayRate,
        "emma": rate_emma.EmmaRate,
        "dimbo": rate_dimbo.DimboRate,
        "dom": rate_dom.DomRate,
        "sub": rate_dom.DomRate,
        "fish": rate_fish.FishRate,
        "cute": rate_cute.CuteRate,
        "bottom": rate_bottom.BottomRate,
        "stinky": rate_stinky.StinkyRate,
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot

    async def respond(
        self, message: discord.Message, target: discord.Member, match=re.Match
    ):
        topic = match.group(1).strip()

        # this will ignore words that include 'rate' such as 'separate', 'celebrate', etc.
        check_for_ignore = f"{topic.lower()}rate"
        if check_for_ignore in IGNORE_WORDS:
            self.parent.logger.debug(
                f"Ignoring {check_for_ignore} as it is in the ignore list."
            )
            return

        if topic.lower() in self.rate_classes:
            responder_class = self.rate_classes.get(topic.lower())
            responder = responder_class(self.parent, self.bot)
        # special case for rate anything
        else:
            responder_class = rate_anything.RateAnything
            responder = responder_class(
                self.parent, self.bot, target=target, topic=topic
            )

        self.parent.logger.debug(
            f"Calling respond method from {responder_class.__name__}"
        )
        await responder.respond(message, target, match)
