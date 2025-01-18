"""Rate Responder

This is the parent class for all rate responders. It will respond to any
trigger containing 'rate'. It will then call the appropriate rate
responder class based on the topic provided.

When creating new rate responder classes, be sure to add them to imports
and the 'rate_classes' mapping.
"""

import re

import discord
from redbot.core.bot import Red

from . import (
    rate_anything,
    rate_bottom,
    rate_berry,
    rate_cute,
    rate_dimbo,
    rate_dom,
    rate_emma,
    rate_fish,
    rate_gay,
    rate_stinky,
)
from .base_text_responder import BaseTextResponder


class RateResponder(BaseTextResponder):
    enabled: bool = True
    # \A: Asserts the position at the start of the string.
    # ([\w\s]+): Captures one or more word characters (letters, digits, and underscores) or spaces as the first word or words.
    # \s+: Matches one or more whitespace characters.
    # rate: Matches the literal string "rate".
    # \s*: Matches zero or more whitespace characters.
    # \Z: Asserts the position at the end of the string.
    patterns: list[str] = [r"\A([\w\s]+)\s+rate\s*\Z"]
    ignore_case: bool = True

    # Mapping of topics to their respective rate responder classes
    # This is done manually right now, but it could be automated using
    # filenames and class names in the future.
    rate_classes = {
        "bottom": rate_bottom.BottomRate,
        "berry": rate_berry.BerryRate,
        "cute": rate_cute.CuteRate,
        "dimbo": rate_dimbo.DimboRate,
        "dom": rate_dom.DomRate,
        "emma": rate_emma.EmmaRate,
        "fish": rate_fish.FishRate,
        "gay": rate_gay.GayRate,
        "stinky": rate_stinky.StinkyRate,
        "sub": rate_dom.DomRate,
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot

    async def respond(
        self, message: discord.Message, target: discord.Member, match=re.Match
    ):
        topic = match.group(1).strip()

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
