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
    # matches "long"/"short" "cat" or "kitty" capturing the "o"s in a group
    patterns = [r"\bl(o+)ng|sh(o*)rt (cat)|(kitty)\b"]
    ignore_case = True

    EMOJI_CAT_FRONT = "<:longcat_1:948672953715929168>"
    EMOJI_CAT_MIDDLE = "<:longcat_2:948672968073031690>"
    EMOJI_CAT_END = "<:longcat_3:948672983067680798>"
    EMOJI_KNIFE = ":knife:"

    MAX_SECTIONS = 5
    HALF_SECTIONS = MAX_SECTIONS // 2
    DEFAULT_SECTIONS = 3

    def __init__(self, parent, bot: Red):
        # BaseTextResponder is an abstract class which does not have an
        # init, so don't call super().__init__ here.
        self.parent = parent
        self.bot = bot

        self.never_respond.extend([const.KIRIN_ID])

        # start with 3 sections for long cat.
        self.sections = self.DEFAULT_SECTIONS

    async def respond(
        self,
        message: discord.Message,
        target: discord.Member,
        match: re.Match,
    ):

        # captures "o"s in either "long" or "short"
        ooo = match.group(1) or match.group(2)
        name = match.group(3) or match.group(4)

        # we only want to add or remove sections if more than one 'o' is
        # captured, otherwise we just want to display the current long cat.
        if match.group(1) and len(ooo) > 1:
            self.sections += len(ooo)
        elif match.group(2) and len(ooo) > 1:
            self.sections -= len(ooo)

        middle_cat = "".join([self.EMOJI_CAT_MIDDLE] * self.sections)
        long_cat = f"{self.EMOJI_CAT_FRONT}{middle_cat}{self.EMOJI_CAT_END}"

        if self.sections > self.MAX_SECTIONS:
            middle_cat = "".join([self.EMOJI_CAT_MIDDLE] * self.HALF_SECTIONS)
            middle_cat = (
                f"{self.EMOJI_CAT_MIDDLE}{self.EMOJI_KNIFE}{self.EMOJI_CAT_MIDDLE}"
            )
            long_cat = f"{self.EMOJI_CAT_FRONT}{middle_cat}{self.EMOJI_CAT_END}"

            await self.send_message(message, long_cat, as_reply=False, delay=False)
            await self.send_message(
                message, "OH NO! LONG CAT WAS TOO LONG!", as_reply=True, delay=False
            )
            self.sections = self.DEFAULT_SECTIONS
        elif self.sections < 0:
            long_cat = f"{self.EMOJI_CAT_END}{self.EMOJI_CAT_FRONT}"

            await self.send_message(message, long_cat, as_reply=False, delay=False)
            await self.send_message(
                message, "OH NO! LONG CAT WAS TOO SHORT!", as_reply=True, delay=False
            )
            self.sections = self.DEFAULT_SECTIONS
        else:
            await self.send_message(message, long_cat, as_reply=False, delay=False)
