"""Table Unflip Responder

Simple call/response responder that unflips tables.
"""

import random
import re

import discord
from redbot.core.bot import Red

from .base_text_responder import BaseTextResponder
from .. import const


class LongCatResponder(BaseTextResponder):
    enabled = True
    patterns = [r"\blong cat\b", r"\blong kitty\b"]
    ignore_case = True

    EMOJI_CAT_FRONT = "<:longcat_1:948672953715929168>"
    EMOJI_CAT_MIDDLE = "<:longcat_2:948672968073031690>"
    EMOJI_CAT_END = "<:longcat_3:948672983067680798>"
    EMOJI_KNIFE = ":knife:"

    def __init__(self, parent, bot: Red):
        super().__init__()
        self.parent = parent
        self.bot = bot

        self.never_respond.extend([const.KIRIN_ID])

    async def respond(
        self,
        message: discord.Message,
        target: discord.Member,
        match: re.Match,
    ):
        sections = random.randint(0, 3)
        middle_cat = "".join([self.EMOJI_CAT_MIDDLE] * sections)
        long_cat = f"{self.EMOJI_CAT_FRONT}{middle_cat}{self.EMOJI_CAT_END}"

        if random.random() < 0.5:
            long_cat = f"{self.EMOJI_CAT_FRONT}{self.EMOJI_KNIFE}{self.EMOJI_CAT_END}"

        await self.send_message(message, long_cat, as_reply=False, delay=False)
