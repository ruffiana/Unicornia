""" I'm Your Daddy

Responds to "I'm [blank]" or "I am [blank]" with "Hi, [blank]! I'm your daddy..."
"""

import random
import re

import discord
from redbot.core.bot import Red

from .base_text_responder import BaseTextResponder
from .. import const


class ImDaddyResponder(BaseTextResponder):
    enabled = True
    # Match "i'm | i am" at the beginning of the message
    patterns = [r"\A(?:i'?\s?a?m\s+)"]
    ignore_case = True

    def __init__(self, parent, bot: Red):
        # BaseTextResponder is an abstract class which does not have an
        # init, so don't call super().__init__ here.
        self.parent = parent
        self.bot = bot

        self.always_respond.extend(
            [
                # berry
                1058458210060751039
            ]
        )

    async def respond(
        self,
        message: discord.Message,
        target: discord.Member,
        match: re.Match,
    ):
        if message.author.id in self.never_respond:
            return

        name = message.content[match.end() :].strip()

        chance = 50 / max(1, len(name))
        self.parent.logger.debug(f"{name} = {chance}% chance to respond")

        if message.author.id in self.always_respond or random.randint(0, 99) < chance:
            daddy_response = f"Hi, {name}! I'm your daddy..."
            if message.author.id == const.RUFFIANA_ID:
                daddy_response = self.parent.uwu_cog.translate(daddy_response)

            await self.send_message(message, daddy_response, as_reply=True, delay=True)
