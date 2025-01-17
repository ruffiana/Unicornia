import random
import re

import discord
from redbot.core.bot import Red

from .text_responder_base import TextResponderBase


class ImDaddyResponder(TextResponderBase):
    enabled = True
    # Match "i'm | i am" at the beginning of the message
    pattern = r"\A(?:i'?\s?a?m\s+)"
    ignore_case = True

    # List of user IDs that will always get a response
    always_respond = [474075064069783552]
    # List of user IDs that will never get a response
    never_respond = []

    def __init__(self, parent, bot: Red):
        super().__init__()
        self.parent = parent
        self.bot = bot

    async def respond(self, message: discord.Message, target: discord.Member = None):
        if message.author.id in self.never_respond:
            return

        match = re.match(self.pattern, message.content, self.regex_flags)
        name = message.content[match.end() :].strip()

        chance = 50 / max(1, len(name))
        self.parent.logger.debug(f"{name} = {chance}% chance to respond")

        if message.author.id in self.always_respond or random.randint(0, 99) < chance:
            await self.send_message(
                message, f"Hi, {name}! I'm your daddy...", as_reply=True, delay=True
            )
