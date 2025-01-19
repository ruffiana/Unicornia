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
from .base_rate_responder import BaseRateResponder
from pathlib import Path


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

    RATE_RESPONDER_PATH = Path(__file__).parent

    def __init__(self, parent, bot: Red):
        # BaseTextResponder is an abstract class which does not have an
        # init, so don't call super().__init__ here.
        self.parent = parent
        self.bot = bot

        # Mapping of topics to their respective rate responder classes
        # This is done manually right now, but it could be automated using
        # filenames and class names in the future.
        self.rate_classes = {
            "bottom": rate_bottom.BottomRate(parent, bot),
            "berry": rate_berry.BerryRate(parent, bot),
            "cute": rate_cute.CuteRate(parent, bot),
            "dimbo": rate_dimbo.DimboRate(parent, bot),
            "dom": rate_dom.DomRate(parent, bot),
            "emma": rate_emma.EmmaRate(parent, bot),
            "fish": rate_fish.FishRate(parent, bot),
            "gay": rate_gay.GayRate(parent, bot),
            "stinky": rate_stinky.StinkyRate(parent, bot),
        }

        # Default rate responder class
        self.rate_classes["default"] = rate_anything.RateAnything(parent, bot)

        # Aliasing topics
        # TODO: there's probably a smarter way to do this, but this is the easiest right now
        self.rate_classes["sub"] = self.rate_classes["dom"]

    async def respond(
        self, message: discord.Message, target: discord.Member, match=re.Match
    ):
        topic = match.group(1).strip()

        # this attempts to get the appropriate responder object based on
        # the topic. It will default to the RateAnything object if the
        # topic is not found
        responder = self.rate_classes.get(
            topic.lower(), self.rate_classes.get("default")
        )

        responder.topic = topic

        self.parent.logger.debug(
            f"Calling respond method from {responder.__class__.__name__}"
        )
        await responder.respond(message, target=target, match=match)
